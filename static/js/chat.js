const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값


window.onload = async function () {
    if (!access_token) {
        alert('로그인 시 이용이 가능합니다.')
        window.location.href = `${backend_base_url}`
    }
    let userId = getUserIdFromAccessToken(access_token);
    let is_seller = false;

    let chat_uer = localStorage.getItem("chat_user");
    let store_id = localStorage.getItem("store_id");
    let store_name = localStorage.getItem("store_name");
    let chat_image = localStorage.getItem("chat_image");
    let chat_user_name = localStorage.getItem("chat_user_name");
    if (chat_uer) {
        userId = chat_uer
    }
    const parts = window.location.href.split('/');
    const nonEmptyParts = parts.filter(part => part.length > 0);

    const storeId = nonEmptyParts[nonEmptyParts.length - 1];
    if (store_id === storeId) {
        is_seller = true;
    }

    let start_html = `
                <div class="user_img w3" style="background: url(${chat_image})"></div>
                <p><span>${chat_user_name}</span>과 실시간 채팅이 시작됐어요!</p>
        `;

    if (!chat_image || chat_image === 'false') {
        start_html = `
                <div class="user_img w3 empty"></div>
                <p><span>${chat_user_name}</span>과 실시간 채팅이 시작됐어요!</p>
        `;
    }

    $('#chat_start_ment').append(start_html);

    const chatSocket = new WebSocket(
        (window.location.protocol === "https:" ? "wss://" : "ws://")
        + window.location.host
        + '/ws/chat/'
        + storeId
        + '/'
        + userId
        + '/'
    );
    let defultImage = staticPath + 'profile.svg';
    let chatLog = $('.real-time');
    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        let user_id = localStorage.getItem('user_id')
        if (data.messages) {
            // If 'messages' are received, it is the initial load of past messages
            let temp_html = ''
            data.messages.forEach((msgContent) => {
                if (msgContent['caller'] === user_id) {
                    temp_html = `
                                <li class="opponent">
                                <li class="my"><p>${msgContent.message}</p></li>
                                `
                } else {
                    if (chat_image && chat_image !== 'false') {
                        temp_html = `<li class="opponent">
                                        <div class="user_img w4" style="background: url(${chat_image})">
                                        </div>
                                        <div class="width">
                                            <p>
                                                ${msgContent.message}
                                            </p>
                                        </div>
                                    </li>
                                `
                    } else {
                        temp_html = `<li class="opponent">
                                        <div class="user_img w4 empty">
                                        </div>
                                        <div class="width">
                                            <p>
                                                ${msgContent.message}
                                            </p>
                                        </div>
                                    </li>
                                `
                    }
                }

                // <span class="name">${msgContent['name']}</span>

                $('#chat-log').append(temp_html);
                // 메시지를 추가한 후 스크롤을 최하단으로 이동
                setTimeout(function () {
                    chatLog.scrollTop(chatLog.prop('scrollHeight'));
                }, 100); // 100 밀리초 후에 실행
                // document.querySelector('#chat-log').value += (msgContent['caller'] + ': ');
                // document.querySelector('#chat-log').value += (msgContent.message + '\n');
            });
        } else if (data.message) {
            // 채팅 로그 요소
            if (data['caller']) {
                let caller = data['caller']
                let name = data['name']
                let msg = data.message
                let temp_html = ''
                if (data['caller'] * 1 === user_id * 1) {
                    temp_html = `
                                <li class="opponent">
                                <li class="my"><p>${msg}</p></li>
                                `
                } else {
                    temp_html = `<li class="opponent">
                                        <div class="user_img w4 empty"">
                                        </div>
                                        <div class="width">
                                            <p>
                                                ${msg}
                                            </p>
                                        </div>
                                    </li>
                                `
                    if (chat_image && chat_image !== 'false') {
                        temp_html = `<li class="opponent">
                                        <div class="user_img w4" style="background: url(${chat_image})">
                                        </div>
                                        <div class="width">
                                            <p>
                                                ${msg}
                                            </p>
                                        </div>
                                    </li>
                                `
                    }
                }
                $('#chat-log').append(temp_html);
                // 메시지를 추가한 후 스크롤을 최하단으로 이동
                setTimeout(function () {
                    chatLog.scrollTop(chatLog.prop('scrollHeight'));
                }, 100); // 100 밀리초 후에 실행
            }
        }
    };
    chatSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };

    document.querySelector('#chat-message-input').onkeyup = function (e) {
        if (e.key === 'Enter') {  // enter, return
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            if (message !== "") {
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'store_id': storeId,
                    'user_id': userId,
                    'is_seller': is_seller,
                }));
                messageInputDom.value = '';
            }
        }
    };

    document.querySelector('#chat-message-submit').onclick = function (e) {
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        if (message !== "") {
            chatSocket.send(JSON.stringify({
                'message': message,
                'store_id': storeId,
                'user_id': userId,
                'is_seller': is_seller,
            }));
            messageInputDom.value = '';
        } else {
            return false
        }
    };
    // 메시지를 추가한 후 스크롤을 최하단으로 이동
    setTimeout(function () {
        chatLog.scrollTop(chatLog.prop('scrollHeight'));
    }, 300); // 100 밀리초 후에 실행

};


function getUserIdFromAccessToken(accessToken) {
    const payload = accessToken.split('.')[1];

    const decodedPayload = atob(payload);

    const payloadObj = JSON.parse(decodedPayload);

    return payloadObj.user_id;
}


function reloadChatArea() {
    $('#chat_box').load(window.location.href + "#chat_box");
}