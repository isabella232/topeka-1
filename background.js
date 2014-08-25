'use strict';

/******************************************************************************/

chrome.app.runtime.onLaunched.addListener(function() {
  chrome.app.window.create('index.html', {
    width: 244,
    height: 380,
  });
});

/******************************************************************************/

chrome.notifications.onClosed.addListener(function(notificationId) {
  console.log('onClosed fired. notificationId =', notificationId);
});

chrome.notifications.onClicked.addListener(function(notificationId) {
  console.log('onClicked fired. notificationId =', notificationId);

  chrome.notifications.clear(notificationId, function(wasCleared) {
  });
});

chrome.notifications.onButtonClicked.addListener(function(notificationId, buttonIndex) {
  console.log('onButtonClicked fired. notificationId =', notificationId, ', buttonIndex =', buttonIndex);
});

/******************************************************************************/

function createLocalNotification(notificationId, options, callback) {
  options.iconUrl = options.iconUrl || '';
  options.message = options.message || 'Eh';
  callback = callback || function() {}
  chrome.notifications.create(notificationId, options, callback);
}

/******************************************************************************/

chrome.gcm.onMessage.addListener(function(msg) {
  if (typeof msg.data.type !== 'string') {
    console.error('Invalid message format:', JSON.stringify(msg, null, 2));
    return;
  }

  switch(msg.data.type) {
    case 'scoreBeaten': {
      onScoreBeaten(JSON.parse(msg.data));
      break;
    };
    default: {
      console.error('Invalid message type:', JSON.stringify(msg, null, 2));
      return;
    }
  }
});

function onScoreBeaten(data) {
  chrome.notifications.create('topeka-score-beaten', {
      type:'basic',
      title:'Topeka',
      iconUrl: 'icons/Icon-72.png',
      message: 'Your Score on Topeka was beaten by ' + data.user,
    }, function() { });
}

/******************************************************************************/

chrome.gcm.onSendError.addListener(function() {
  console.error.apply(console, arguments);
});

chrome.gcm.onMessagesDeleted.addListener(function() {
  console.error.apply(console, arguments);
});

/******************************************************************************/
