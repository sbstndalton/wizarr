"""Synthetic validation only; no real invitations, accounts, or remote API calls."""
from flask import Flask, request, session
from werkzeug.datastructures import MultiDict
from app.forms.join import JoinForm
from app.forms.admin import _password_validators as PASSWORD_VALIDATORS
from app.services.invitation_flow.strategies import FormBasedStrategy
from pathlib import Path

app=Flask(__name__)
app.config.update(SECRET_KEY='synthetic-test-only', WTF_CSRF_ENABLED=False)
app.add_url_rule('/j/<code>',endpoint='public.invite',view_func=lambda code:code)
checks=0
def check(value,message):
 global checks
 assert value,message
 checks+=1
 print('PASS',message)
from app.blueprints.api.api_routes import _generate_invitation_url
from app.config import ProductionConfig
check(hasattr(ProductionConfig,'WIZARR_PUBLIC_URL'),'production config exposes public invitation URL setting')
with app.test_request_context('/',base_url='http://127.0.0.1:5690'):
 check(_generate_invitation_url('SYNTH12345')=='/j/SYNTH12345','unconfigured API URL remains compatible')
 app.config['WIZARR_PUBLIC_URL']='https://invites.example.invalid/'
 check(_generate_invitation_url('SYNTH12345')=='https://invites.example.invalid/j/SYNTH12345','API returns full configured public invitation URL')
 app.config['WIZARR_PUBLIC_URL']='javascript:invalid'
 check(_generate_invitation_url('SYNTH12345')=='/j/SYNTH12345','invalid public URL falls back without leaking internal host')
 app.config['WIZARR_PUBLIC_URL']=''
with app.test_request_context('/j/SYNTH12345?username=Prefill.Test'):
 check(JoinForm().username.data=='Prefill.Test','request name prefilled')
with app.test_request_context('/j/SYNTH12345'):
 request.view_args={'code':'SYNTH12345'}
 session['invite_prefill_code']='SYNTH12345';session['invite_prefill_username']='Saved.Name'
 check(JoinForm().username.data=='Saved.Name','name survives pre-invite wizard redirects')
with app.test_request_context('/j/OTHER12345'):
 request.view_args={'code':'OTHER12345'}
 session['invite_prefill_code']='SYNTH12345';session['invite_prefill_username']='Saved.Name'
 check(not JoinForm().username.data,'saved name is scoped to its invitation')
with app.test_request_context('/j/SYNTH12345?username=Full%20Name'):
 check(JoinForm().username.data=='Full.Name','full name normalized to username format')
with app.test_request_context('/j/SYNTH12345?username=A'):
 check(JoinForm().username.data=='A__','short name padded to existing username minimum')
base={'username':'synthetic','code':'SYNTH12345','password':'x','confirm_password':'x'}
with app.test_request_context('/invitation/process',method='POST'):
 f=JoinForm(formdata=MultiDict(base))
 check(f.validate(), 'one-character guest password and no email accepted: '+str(f.errors))
 check(not JoinForm(formdata=MultiDict({**base,'confirm_password':'y'})).validate(),'confirmation mismatch rejected')
 check(not JoinForm(formdata=MultiDict({**base,'password':'','confirm_password':''})).validate(),'empty password rejected')
 check(not JoinForm(formdata=MultiDict({**base,'password':'x'*129,'confirm_password':'x'*129})).validate(),'technical 128-character limit retained')
 check(JoinForm(formdata=MultiDict({**base,'password':'word','confirm_password':'word'})).validate(),'no uppercase/number complexity rule')
 ok,_,_=FormBasedStrategy().authenticate([],base)
 check(ok,'invitation strategy accepts no email')
with app.test_request_context('/j/SYNTH12345?username=Original.Name',method='POST'):
 check(JoinForm(formdata=MultiDict(base)).username.data=='synthetic','applicant can edit prefilled username')
check(any(getattr(v,'min',None)==8 for v in PASSWORD_VALIDATORS),'admin password requirements unchanged')
check('form.email(' not in Path('/app/app/templates/welcome-jellyfin.html').read_text(),'email field absent from Jellyfin signup')
check('name="email"' not in Path('/app/app/templates/hybrid-password-form.html').read_text(),'email field absent from hybrid signup')
from app.extensions import db
import app.services.media.jellyfin as jellyfin
from app.models import User
app.config.update(SQLALCHEMY_DATABASE_URI='sqlite://',SQLALCHEMY_TRACK_MODIFICATIONS=False)
db.init_app(app)
with app.app_context():
 db.create_all()
 db.session.add(User(token='synthetic',username='existing',email='',code='SYNTH12345'))
 db.session.commit()
 class SyntheticClient:
  server_id=None
  reached=False
  def create_user(self,username,password):
   self.reached=True
   raise RuntimeError('Synthetic backend boundary; no real media API called')
 client=SyntheticClient()
 original=jellyfin.is_invite_valid
 jellyfin.is_invite_valid=lambda code:(True,'synthetic invitation')
 try:
  from unittest.mock import patch
  with patch.object(jellyfin.logging,'error'):
   jellyfin.JellyfinClient._do_join(client,'another','x','x','','SYNTH12345')
  check(client.reached,'short password without email passes backend validation; blank emails do not collide')
 finally:jellyfin.is_invite_valid=original
print(checks,'synthetic Wizarr checks passed')

