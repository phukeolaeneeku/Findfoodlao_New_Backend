let backend_base_url = 'http://127.0.0.1:8000'
let domain = ''

if (window.location.href.includes('humascot.shop')) {
    backend_base_url = 'https://humascot.shop'
    domain = 'humascot.shop'
} else if (window.location.href.includes('web4all.site')) {
    backend_base_url = 'https://web4all.site'
    domain = 'web4all.site'
} else if (window.location.href.includes('web4all.store')) {
    backend_base_url = 'https://web4all.store'
    domain = 'web4all.store'
}

function redirectURL() {
    var useragt = navigator.userAgent.toLowerCase();
    var target_url = location.href;
    if (useragt.match(/kakaotalk/i)) {
        //카카오톡 외부브라우저로 호출
        location.href = 'kakaotalk://web/openExternal?url=' + encodeURIComponent(target_url);

    }
    if (navigator.userAgent.match
    (/inapp|NAVER|KAKAOTALK|Snapchat|Line|WirtschaftsWoche|Thunderbird|Instagram|everytimeApp|WhatsApp|Electron|wadiz|AliApp|zumapp|iPhone(.*)Whale|Android(.*)Whale|kakaostory|band|twitter|DaumApps|DaumDevice\/mobile|FB_IAB|FB4A|FBAN|FBIOS|FBSS|SamsungBrowser\/[^1]/i,)
    ) {
        // document.body.innerHTML = "";
        if (navigator.userAgent.match(/iPhone|iPad/i)) {
            // IOS
            location.href = `ftp://${domain}/?_targeturl=` + location.href;
            /*
            FTP - File Transfer Protocol
            (서버와 클라이언트 사이의 파일 전송을 하기 위한 프로토콜)

            ios에서는 FTP 프로토콜을 호출하여 자동으로 사파리가 열리게 되는 현상
            (익명이 접근 가능해야 함)

            FTP 프로토콜을 웹에서 실행함으로써 ios 운영체제에서
            강제로 사파리를 실행시키게 되며,
            사파리가 FTP 내 html을 읽어서 강제로 페이지를 이동시킴
            */
        } else {
            // 안드로이드
            location.href = "intent://" +
                location.href.replace(/https?:\/\//i, "") +
                "#Intent;scheme=https;package=com.android.chrome;end";
            /*
              페이지를 강제 이동시켜서 크롬으로 URL을 열 수 있게 가능
                안드로이드의 intent 속성
              안드로이드폰에 크롬이 이미 내장되어 있어 브라우저를 크롬 패키지로 설정
            */
        }
    }
}

// redirectURL()

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function chatList() {
    const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
    if (access_token) {
        window.location.href = `${backend_base_url}/chat`;
    } else {
        alert('로그인 후 사용해주세요.')
        window.location.href = '/store/goods/list'
    }
};


async function orderList() {
    const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
    if (access_token) {
        window.location.href = `${backend_base_url}/store/order/list`;
    } else {
        alert('로그인 후 사용해주세요.')
        // window.location.href = '/store/goods-list'
    }
};


async function goodsList() {
    const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
    if (access_token) {
        window.location.href = `${backend_base_url}/store/goods/list`;
    } else {
        alert('로그인 후 사용해주세요.')
        // window.location.href = '/store/goods-list'
    }
};

async function morePage() {
    const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
    if (access_token) {
        window.location.href = `${backend_base_url}/user/more`;
    } else {
        alert('로그인 후 사용해주세요.')
        // window.location.href = '/store/goods-list'
    }
};


async function userProfile() {
    const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
    if (access_token) {
        window.location.href = `${backend_base_url}/user/profile`;
    } else {
        alert('로그인 후 사용해주세요.')
        // window.location.href = '/store/goods-list'
    }
};
