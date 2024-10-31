window.onload = async function () {
    await loadGoodsList()
    let is_first = localStorage.getItem('is_first')
    if (is_first) {
        modal.style.display = "flex"; // 모달 표시
    }

    let storeId = localStorage.getItem('store_id')
    if (document.getElementById('admin_store_render')) {
        if (!storeId) {
            document.getElementById('admin_store_render').style.display = 'none';
        } else {
            document.getElementById('admin_store_render').style.display = 'block';
        }
    }
}

async function changeUserToSeller() {
    window.location.href = '/user/seller-signup'
}

async function loadGoodsList(category = null) {
    let url = `${backend_base_url}/store?category=1`
    if (category) {
        url = `${backend_base_url}/store?category=${category}`
    }
    const response = await fetch(`${url}`, {
        headers: {
            'content-type': 'application/json',
        },
        method: 'GET',
    });
    let response_json = await response.json()
    if (response.ok) {
        $('#goods_list').empty();
        await goodsListParse(response_json)

        // if (!category) {
        //     const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
        //     if (access_token) {
        //         let temp_html = `<a onclick="logOut()" style="text-decoration: none">로그 아웃</a>`
        //         $('#user-bar').append(temp_html);
        //     } else {
        //         let temp_html = `<a href="/user/signin" style="text-decoration: none">로그인 하러가기</a>`
        //         $('#user-bar').append(temp_html);
        //     }
        // }
    }
    const ul = document.querySelector(".product_list ul");
    const moreButton = document.getElementById("moreButton");
    const liItems = ul.querySelectorAll("li");
    let currentIndex = 8;
    let blockCount = 0;

    liItems.forEach((li) => {
        if (window.getComputedStyle(li).display === 'block') {
            blockCount++;
        }
    });
    if (blockCount >= 8) {
        moreButton.addEventListener("click", function () {
            for (let i = currentIndex; i < currentIndex + 8; i++) {
                if (liItems[i]) {
                    liItems[i].style.display = "block";
                }
            }
            currentIndex += 8;

            // 모든 li 요소가 표시될 경우 더보기 버튼 숨김
            if (currentIndex >= liItems.length) {
                moreButton.style.display = "none";
            }
        });
    } else {
        moreButton.style.display = 'none';
    }

}

async function orderByPrice() {
    await loadGoodsList(2)  // 가격순으로 변경
    document.getElementById("orderby_review").className = ''
    document.getElementById("orderby_price").className = 'on'
    document.getElementById("orderby_low_review").className = ''
    document.getElementById("orderby_sell").className = ''
    document.getElementById("orderby_create").className = ''
}

async function orderByReview() {
    await loadGoodsList(3)  // 리뷰순으로 변경
    document.getElementById("orderby_review").className = 'on'
    document.getElementById("orderby_price").className = ''
    document.getElementById("orderby_low_review").className = ''
    document.getElementById("orderby_sell").className = ''
    document.getElementById("orderby_create").className = ''
}

async function orderByLowReview() {
    await loadGoodsList(4)  // 낮은 가격순으로 변경
    document.getElementById("orderby_review").className = ''
    document.getElementById("orderby_price").className = ''
    document.getElementById("orderby_low_review").className = 'on'
    document.getElementById("orderby_sell").className = ''
    document.getElementById("orderby_create").className = ''

}


async function orderBySell() {
    await loadGoodsList(5)  // 판매순으로 변경
    document.getElementById("orderby_review").className = ''
    document.getElementById("orderby_price").className = ''
    document.getElementById("orderby_low_review").className = ''
    document.getElementById("orderby_sell").className = 'on'
    document.getElementById("orderby_create").className = ''

}


async function orderByCreate() {
    await loadGoodsList(6)  // 최신순으로 변경
    document.getElementById("orderby_review").className = ''
    document.getElementById("orderby_price").className = ''
    document.getElementById("orderby_low_review").className = ''
    document.getElementById("orderby_sell").className = ''
    document.getElementById("orderby_create").className = 'on'
}


async function search() {
    let search = document.getElementById("search").value
    const response = await fetch(`${backend_base_url}/store/search`, {
        headers: {
            'content-type': 'application/json',
        },
        body: JSON.stringify({'search': search}),
        method: 'POST',
    });
    let response_json = await response.json()
    if (response.ok) {
        $('#goods_list').empty();
        await goodsListParse(response_json)
        console.log(response_json)
    }
}

async function goodsListParse(response_json) {
    let defultImage = staticPath + 'thum.png';
    await response_json.forEach((data) => {
        console.log(data)
        let category = data['category'];
        let id = data['id'];
        let image = data['image'];
        let name = data['name'];
        let price = data['format_price'];
        let star_avg = data['star_avg'];  // 나중에 아이콘 개수 맞추기
        star_avg = star_avg / 5 * 100
        if (star_avg === 0) {
            star_avg = 100
        }
        let store_address = data['store_address'];
        let store_name = data['store_name'];

        let temp_html = `
                                    <li>
                                        <div class="thum">
                                            <img onclick='javascript:location.href="/store/goods/detail/${id}"' src="${defultImage}" alt=""/>
                                        </div>
                                        <div class="info mt20">
                                            <div class="star">
                                                <div class="on" style="width: ${star_avg}%;"></div>
                                            </div>
                                            <div class="flex">
                                                <div class="category">${category}</div>
                                                <div class="cost">${price}</div>
                                            </div>
                                            <div class="name">${name}</div>
                                            <div class="address">${store_address}</div>
                                        </div>
                                    </li>
                                    `
        if (image) {
            temp_html = `
                                <li>
                                    <div class="thum">
                                        <img onclick='javascript:location.href="/store/goods/detail/${id}"' src="${image}" alt=""/>
                                    </div>
                                    <div class="info mt20">
                                        <div class="star">
                                            <div class="on" style="width: ${star_avg}%;"></div>
                                        </div>
                                        <div class="flex">
                                            <div class="category">${category}</div>
                                            <div class="cost">${price}</div>
                                        </div>
                                        <div class="name">${name}</div>
                                        <div class="address">${store_address}</div>
                                    </div>
                                </li>
                                `
        }
        $('#goods_list').append(temp_html);
    });
}