const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
const user_id = localStorage.getItem('user_id')  //요청시 필요한 토큰 값
window.onload = async function () {
    const response = await fetch(`${backend_base_url}/chat/list`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${access_token}`,
        },
        method: 'GET',
    });

    let response_json = await response.json()
    $('#chat_list').empty();
    if (response_json.length === 0) {
        console.log(document.getElementById('empty'))
        document.getElementById('empty').style.display = 'block';
    } else {
        document.getElementById('empty').style.display = 'none';
        let defultImage = staticPath + 'profile.svg';
        await response_json.forEach((data) => {
            let store_name = data['store_name'];
            let last_message = data['last_message'];
            let store_id = data['store'];
            let user_name = data['user_name'];
            let chat_image = data['user_profile']
            let customer_id = data['user'];
            if (customer_id * 1 === user_id * 1) {
                user_name = store_name
                chat_image = data['store_image']
            }
            let chat_user_name = user_name
            let temp_html = `
                                    <li  onclick="chatRoom(${store_id}, ${customer_id}, '${store_name}', '${chat_user_name}','${chat_image}')">
                                        <div class="img empty">
                                            <img src="${defultImage}" alt=""/>
                                        </div>
                                        <div class="txt">
                                            <span class="name">${user_name}</span>
                                            <p>
                                                ${last_message}
                                            </p>
                                        </div>
                                    </li>
                                    `;
            if (chat_image && chat_image !== 'false') {
                temp_html = `
                                    <li  onclick="chatRoom(${store_id}, ${customer_id}, '${store_name}', '${chat_user_name}','${chat_image}')">
                                        <div class="img user_img" style="background: url(${chat_image})">
                                        </div>
                                        <div class="txt">
                                            <span class="name">${user_name}</span>
                                            <p>
                                                ${last_message}
                                            </p>
                                        </div>
                                    </li>`
            }
            $('#chat_list').append(temp_html);
        });
    }
    console.log(response_json)
}


async function chatRoom(store_id, user_id, store_name, chat_user_name, chat_image) {
    if (access_token) {
        localStorage.setItem("chat_user", user_id);
        localStorage.setItem("store_name", store_name);
        localStorage.setItem("chat_user_name", chat_user_name);
        localStorage.setItem("chat_image", chat_image);
        window.location.href = `${backend_base_url}/chat/room/${store_id}`;
    } else {
        alert('로그인 후 사용해주세요.')
        window.location.href = `${backend_base_url}`
    }
};

