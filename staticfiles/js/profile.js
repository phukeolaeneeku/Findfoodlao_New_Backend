window.onload = async function () {
    let profile_name = document.getElementById('user_name')
    let store_name = localStorage.getItem('origin_store_name')
    let user_name = localStorage.getItem('user_name')
    let profile_iamge = localStorage.getItem('image')
    let email = localStorage.getItem('email')
    if (store_name !== 'false') {
        profile_name.innerText = store_name
        // 나중에 판매자로 설정 -> 지금은 확인하기 위해 잠시 주석
        document.getElementById('user_type').innerText = '';
        await sellerInfoLoad();
    } else {
        profile_name.innerText = user_name
    }

    if (profile_iamge !== 'false') {
        let imageUrl = `${profile_iamge}`;
        document.getElementById('user_img').style.backgroundImage = `url('${imageUrl}')`;
        document.getElementById('user_img').className = 'user_img w10';
    }

    document.getElementById('email').value = email;
}

async function changeInfo(category) {
    if (category === 'basic') {
        await changePassword()
    } else if (category === 'seller') {
        await changeSellerInfo()
    }
}

async function changePassword(data = null) {
    let user_data = data
    // 구글 로그인 비밀번호 변경 X
    let origin_password = document.getElementById('origin_password').value
    let password = document.getElementById('password').value
    let password2 = document.getElementById('password2').value
    let image = document.getElementById('file')
    const formData = new FormData();
    formData.append("profile_image", image.files[0]);
    let response = null
    if (image.files[0] !== undefined && (password === '' || password2 === '' || origin_password === '')) {
        response = await fetch(`${backend_base_url}/user/my-page/profile`, {
            method: 'PATCH',
            headers: {
                // 'Content-Type': 'application/json',
                "Authorization": `Bearer ${token}`,
            },
            body: formData,
        })
    } else {
        formData.append("origin_password", origin_password);
        formData.append("password", password);
        formData.append("password2", password2);

        response = await fetch(`${backend_base_url}/user/my-page`, {
            method: 'PATCH',
            headers: {
                // 'Content-Type': 'application/json',
                "Authorization": `Bearer ${token}`,
            },
            body: formData,
        })
    }

    let response_json = await response.json()
    console.log(response_json)
    document.getElementById('error_msg').innerText = response_json['message']
    document.getElementById('error_msg').style.display = 'block'
    if (response_json['image'] !== 'false' && response_json['image'] !== undefined) {
        localStorage.setItem('image', response_json['image'])
    }
    if (response.ok && !data) {
        morePage()
    }
}

async function changeUserToSeller() {
    window.location.href = '/user/change-seller';
}

async function sellerInfoLoad() {
    const response = await fetch(`${backend_base_url}/user/my-page`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${token}`,
        },
        method: 'GET',
    });
    let response_json = await response.json()
    let address = response_json['store_info']['address']
    let sub_address = response_json['store_info']['sub_address']
    let company_number = response_json['store_info']['company_number']
    let introduce = response_json['store_info']['introduce']
    let phone = response_json['store_info']['phone']
    let name = localStorage.getItem('origin_store_name')
    if (address !== '' && address !== null) {
        document.getElementById('address').value = address;
    }
    if (sub_address !== '' && sub_address !== null) {
        document.getElementById('sub_address').value = sub_address;
    }
    if (company_number !== '' && company_number !== null) {
        document.getElementById('company_number').value = company_number;

    }
    if (introduce !== '' && introduce !== null) {
        document.getElementById('introduce').value = introduce;

    }
    if (phone !== '' && phone !== null) {
        document.getElementById('phone').value = phone;

    }
    if (name !== 'false') {
        document.getElementById('name').value = name;

    }
    document.getElementById('address').style.display = 'block';
    document.getElementById('sub_address').style.display = 'block';
    document.getElementById('postcodify_search_button').style.display = 'block';
    document.getElementById('company_number').style.display = 'block';
    document.getElementById('introduce').style.display = 'block';
    document.getElementById('phone').style.display = 'block';
    document.getElementById('name').style.display = 'block';
    document.getElementById('modify_btn').onclick = function () {
        changeInfo('seller');
    };

}


async function changeSellerInfo() {
    let origin_password = document.getElementById('origin_password').value
    let password = document.getElementById('password').value
    let password2 = document.getElementById('password2').value
    let data = {
        "origin_password": origin_password,
        "password": password,
        "password2": password2
    }
    // 상인 비밀번호 변경
    await changePassword(data)

    let store_id = localStorage.getItem('store_id')
    let store_data = {
        "address": getValueOrFallback('address'),
        "sub_address": getValueOrFallback('sub_address'),
        "company_number": getValueOrFallback('company_number'),
        "introduce": getValueOrFallback('introduce'),
        "phone": getValueOrFallback('phone')
    }

    const response = await fetch(`${backend_base_url}/store/${store_id}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(store_data),
    })
    let response_json = await response.json()
    // if (response_json['image'] !== 'false') {
    //     localStorage.setItem('image', response_json['image'])
    // }
    // alert(response_json['message'])
    document.getElementById('error_msg').innerText = response_json['message']
    document.getElementById('error_msg').style.display = 'block'
    window.location.reload()
}


function getValueOrFallback(elementId) {
    var value = document.getElementById(elementId).value;
    return value === '' ? null : value;
}