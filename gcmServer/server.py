#!/usr/bin/python
import sys, json, random, string
import xmpp

################################################################################

SERVER = 'gcm.googleapis.com'
PORT = 5235
USERNAME = '119557287378'
PASSWORD = 'AIzaSyABJpu8lDTtVgeDwpgNouskBCbbI_L0LAU'

unacked_messages_quota = 1000
send_queue = []
client = None

connected_users = {}

################################################################################

# Return a random alphanumerical id
def random_id():
  rid = ''
  for x in range(8): rid += random.choice(string.ascii_letters + string.digits)
  return rid

################################################################################

def updateScore(regid, data):
  oldscore = 0
  if connected_users.has_key(regid):
    oldscore = connected_users[regid]['score']
  connected_users[regid] = {
    'score': data['score'],
    'name': data['name']
  }
  sendGcmToUsersWhoseScoreWasBeaten(oldscore, data['score'], data['name'])

################################################################################

def sendGcmToUsersWhoseScoreWasBeaten(oldscore, newscore, name):
  # find users with [oldscore, newscore)
  for regid in connected_users.iterkeys():
    user = connected_users[regid]
    if not (user['score'] >= oldscore and user['score'] < newscore):
      return
    sendMessage(regid, {
        'type': 'scoreBeaten',
        'name': name
      })

################################################################################

def sendMessage(to, data):
  send_queue.append({
    'to': to,
    'message_id': random_id(),
    'data': data
  })

################################################################################

def send(json_dict):
  template = "<message><gcm xmlns='google:mobile:data'>{1}</gcm></message>"
  content = template.format(client.Bind.bound[0], json.dumps(json_dict))
  client.send(xmpp.protocol.Message(node = content))
  #print "Sent: " + json.dumps(json_dict, indent=2)

################################################################################

def flush_queued_messages():
  global unacked_messages_quota
  while len(send_queue) and unacked_messages_quota > 0:
    send(send_queue.pop(0))
    unacked_messages_quota -= 1

################################################################################

def message_callback(session, message):
  global unacked_messages_quota
  gcm = message.getTags('gcm')
  if not gcm:
    return
  msg = json.loads(gcm[0].getData())

  # TODO: hangle nack
  if msg.has_key('message_type') and (msg['message_type'] == 'ack' or msg['message_type'] == 'nack'):
    unacked_messages_quota += 1
    return

  # Send ack
  send({
    'to': msg['from'],
    'message_type': 'ack',
    'message_id': msg['message_id']
  })

  if not msg.has_key('data'):
    print "WARNING: No Payload!"
    return

  # TODO: remove this workaround for issue https://github.com/MobileChromeApps/mobile-chrome-apps/issues/290
  payload = None
  if (msg['data'].has_key('payload')):
    payload = json.loads(msg['data']['payload'])
  else:
    payload = msg

  # TODO: remove "test" ping
  if payload['data'].has_key('test'):
    return sendMessage(msg['from'], { 'pong': msg['message_id'] })

  if not payload['data'].has_key('type'):
    print "WARNING: No Message Type!"
    return
  #print "Got: " + json.dumps(payload, indent=2)

  msg_type = payload['data']['type']
  if msg_type == 'updateScore':
    # Add this user to the list of actives
    # TODO: how to prune users? (Perhaps after they fail to ack a message?)
    updateScore(msg['from'], payload['data'])

################################################################################

def main():
  global client
  client = xmpp.Client('gcm.googleapis.com', debug=['socket'])
  client.connect(server=(SERVER, PORT), secure=1, use_srv=False)
  auth = client.auth(USERNAME, PASSWORD)

  if not auth:
    print 'Authentication failed!'
    sys.exit(1)

  client.RegisterHandler('message', message_callback)

  while True:
    client.Process(1)
    flush_queued_messages()

################################################################################

if __name__ == '__main__':
  main()
