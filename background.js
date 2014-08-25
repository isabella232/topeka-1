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
