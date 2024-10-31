const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
async function loadGoodsDetailPage() {
    const parts = window.location.href.split('/');
    const nonEmptyParts = parts.filter(part => part.length > 0);
    const goodsId = nonEmptyParts[nonEmptyParts.length - 1];

    const response = await fetch(`${backend_base_url}/store/detail/${goodsId}`, {
        headers: {
            'content-type': 'application/json',
        },
        method: 'GET',
    });
    let data = await response.json()
    await localstorageSetting(goodsId)
    if (response.ok) {
        // 비우기
        $('#seller_detail').empty();
        $('#product_detail').empty();
        $('#tab01').empty();
        $('#review_list').empty();
        $('#img_set').empty();
        // 각 파트별 파싱
        let store = data['store'];
        let id = data['id'];
        let image_set = data['image_set'];
        let temp_html1 = await sellerDetail(data)
        let temp_html2 = await productDetail(data)
        let temp_html3 = `${data['description']}`
        let temp_html4 = await reviewDetail(data, goodsId)

        // 붙이기
        $('#seller_detail').append(temp_html1);
        $('#product_detail').append(temp_html2);
        $('#tab01').append(temp_html3);
        // $('#review_list').append(temp_html4);

        // 그 외 온클릭 효과 추가
        document.getElementById("review_total").innerText = `리뷰 (${data['review_set'].length})`


        let is_my_store = localStorage.getItem('store_id')
        let store_name = localStorage.setItem('store_name', data['store_name'])
        if (is_my_store * 1 !== store * 1) {
            document.getElementById('chat').onclick = function () {
                chatRoom(store);
            };
            document.getElementById('order').onclick = function () {
                orderRequest(id);
            };
            document.getElementById('user_setting').style.display = 'grid';
        } else {
            document.getElementById('user_setting').style.display = 'none';
            document.getElementById('admin_setting').style.display = 'block';
            document.getElementById('admin_render').onclick = function () {
                window.location.href = '/store/setting'
            };
        }
        // 이미지 슬라이드
        if (image_set.length > 0) {
            image_set.forEach((image) => {
                let temp_html2 = `
                                        <div class="swiper-slide">
                                            <img src="${image}" alt=""/>
                                        </div>
                                        `
                $('#img_set').append(temp_html2);
            });
        } else {

        }
        var swiper = new Swiper(".mySwiper", {
            pagination: {
                el: ".swiper-pagination",
            },
        });

        // 리뷰 페이지 네이션
        const ul = document.querySelector("#tab02 ul");
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
                        // 리뷰 내용 더보기
                        loadReviews()
                        removeMoreButtons()
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
}

async function localstorageSetting(goodsId) {
    const user_id = localStorage.getItem('user_id')  //요청시 필요한 토큰 값
    const response = await fetch(`${backend_base_url}/chat/list/${goodsId}`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${access_token}`,
        },
        method: 'GET',
    });
    let data = await response.json()
    let store_name = data['store_name'];
    let store_id = data['store_id'];
    let user_name = data['user_name'];
    let chat_image = data['user_profile']
    let customer_id = data['user'];
    if (customer_id * 1 === user_id * 1) {
        user_name = store_name
        chat_image = data['store_image']
    }
    let chat_user_name = user_name
    console.log(customer_id, user_id, store_name, chat_user_name)
    localStorage.setItem("chat_user", user_id);
    localStorage.setItem("store_name", store_name);
    localStorage.setItem("chat_user_name", chat_user_name);
    localStorage.setItem("chat_image", chat_image);
}

async function chatRoom(store_id) {
    const storeId = store_id;
    if (access_token) {
        window.location.href = `${backend_base_url}/chat/room/${store_id}`;
    } else {
        alert('로그인 후 사용해주세요.')
        window.location.href = `${backend_base_url}`
    }
};

async function checkReview(goodsId) {
    const response = await fetch(`${backend_base_url}/store/check-review/${goodsId}`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${access_token}`,
        },
        method: 'POST',
    });
    let data = await response.json()
    if (response.ok) {
        return true
    } else {
        return data['message']
    }
}

async function reviewForm(goods_id) {
    const goodsId = goods_id;
    if (access_token) {
        window.location.href = `${backend_base_url}/store/review/form/${goodsId}`;
    } else {
        alert('로그인 후 사용해주세요.')
        // window.location.href = '/store/goods/list'
    }
};


async function orderRequest(goods_id) {
    const goodsId = goods_id;
    if (access_token) {
        const response = await fetch(`${backend_base_url}/store/order`, {
            headers: {
                'content-type': 'application/json',
                "Authorization": `Bearer ${access_token}`,
            },
            body: JSON.stringify({"goods_id": goodsId}),
            method: 'POST',
        });
        if (response.ok) {
            openModal();
        } else {
            let data = await response.json()
            if (data.message) {
                alert(data.message);
            } else if (data['non_field_errors']) {
                alert(data['non_field_errors'][0]);
            }
        }
    } else {
        alert('로그인 후 사용해주세요.')
        // window.location.href = '/store/goods/list'
    }
};

async function sellerDetail(data) {
    let profileImgPath = staticPath + 'profile.svg';
    console.log(data)
    let store_image = data['store_image']
    let temp_html = ''
    if (!store_image || store_image === '' || store_image === 'false') {
        temp_html = `
            <div class="img empty">
                <img src="${profileImgPath}" alt=""/>
            </div>
            <div class="info">
                ${data['store_name']}
                <span>${data['address']}</span>
            </div>
    `
    } else {
        temp_html = `
            <div class="img store_image" style="background: url(${store_image})">
            </div>
            <div class="info">
                ${data['store_name']}
                <span>${data['address']}</span>
            </div>
    `
    }

    return temp_html
}

async function productDetail(data) {
    let star_avg = data['star_avg'];  // 나중에 아이콘 개수 맞추기
    star_avg = star_avg / 5 * 100
    if (star_avg === 0) {
        star_avg = 100
    }
    let temp_html = `
             <div class="name">
                ${data['name']}
                <span>${data['category']}</span>
            </div>
            <div class="flex mt10">
                <div class="cost">${data['price']}</div>
                <div class="star">
                    <div class="on" style="width: ${star_avg}%;"></div>
                </div>
            </div>
    `
    return temp_html
}

async function reviewDetail(data, goodsId) {
    let check_review = checkReview(goodsId).then(result => {
        if (result === true) {
            document.getElementById('review_form').style.display = 'block'
            document.getElementById('review_form').onclick = function () {
                reviewForm(goodsId)
            }
        } else {
            console.log("에러 메시지:", result);
        }
    }).catch(error => {
        console.error("오류 발생:", error);
    });

    let profileImgPath = staticPath + 'profile.svg';
    let temp_html = ''
    if (data['review_set'].length !== 0) {
        data['review_set'].forEach((review) => {
            let star = review['star'];  // 나중에 아이콘 개수 맞추기
            let review_user = review['user'];  // 나중에 아이콘 개수 맞추기
            let user = localStorage.getItem('user_id')
            star = star / 5 * 100
            let temp_html2 = ''
            if (review['profile_image'] !== 'false' && review['profile_image'] != null) {
                temp_html2 = `
                                <li class="review-box">
                                    <div class="box">
                                        <div class="user">
                                            <div class="img">
                                                <img src="${review['profile_image']}" alt="" style="border-radius: 100%"/>
                                            </div>
                                            <div class="name">
                                                ${review['nickname']}
                                                <div class="star">
                                                    <div class="on" style="width: ${star}%;"></div>
                                                </div>
                                            </div>
                                        </div>
                                        <span class="date">${review['created_at']}</span>
                                    </div>
                                    <p class="review-content" id="review_${review['id']}">
                                        ${review['review']}
                                    </p>
                                </li>
                            `

            } else {
                temp_html2 = `
                                <li class="review-box">
                                    <div class="box">
                                        <div class="user">
                                            <div class="img empty">
                                                <img src="${profileImgPath}" alt=""/>
                                            </div>
                                            <div class="name">
                                                ${review['nickname']}
                                                <div class="star">
                                                    <div class="on" style="width: ${star}%;"></div>
                                                </div>
                                            </div>
                                        </div>
                                        <span class="date">${review['created_at']}</span>
                                    </div>
                                    <p class="review-content" id="review_${review['id']}">
                                        ${review['review']}
                                    </p>
                                </li>
                            `
            }

            if (user * 1 === review_user * 1) {
                temp_html2 += `<div class="review_patch_box">
                                    <button id="patch_btn_${review['id']}" class="review_patch_btn" onclick="changePatchInput(${review['id']})">수정</button>
                                    <button id="delete_btn_${review['id']}" class="review_delete_btn" onclick="deleteReview(${review['id']})">삭제</button>
                                </div>`
            }

            temp_html += temp_html2;
            $('#review_list').append(temp_html2);
        });
    } else {
        temp_html = '아직 리뷰가 존재하지 않습니다.'
        $('#review_list').append(temp_html);
    }
    return temp_html
}


async function loadReviews() {
    removeMoreButtons()
    document.getElementById('tab02').style.display = 'block';
    // 리뷰 내용이 DOM에 추가된 후에 "더보기" 버튼 로직 실행
    $('.review-box').each(function () {
        var content = $(this).find('.review-content');
        var maxHeight = 55; // 설정한 최대 높이
        var btn_more = $('<a href="javascript:void(0)" class="more">...더보기</a>');
        $(this).append(btn_more);


        if (content[0].offsetHeight > maxHeight) {
            content.css('max-height', maxHeight + 'px');
            content.css('overflow', 'hidden');
        } else {
            btn_more.hide();
        }

        btn_more.click(function () {
            if (content.css('max-height') != 'none') {
                $(this).html('...접기');
                content.css('max-height', 'none');
            } else {
                $(this).html('...더보기');
                content.css('max-height', maxHeight + 'px');
            }
        });
    });
}

loadGoodsDetailPage()

function removeMoreButtons() {
    $('.review-box').each(function () {
        // 각 리뷰 박스에서 "더보기" 버튼을 찾고 제거
        var btn_more = $(this).find('.more');
        if (btn_more.length) {
            btn_more.remove();
        }

        // 리뷰 콘텐츠의 max-height 스타일 초기화
        var content = $(this).find('.review-content');
        content.css('max-height', '');
        content.css('overflow', '');
    });
}

async function deleteReview(review_id) {
    const response = await fetch(`${backend_base_url}/store/review/${review_id}`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${access_token}`,
        },
        method: 'delete',
    });
    let response_json = await response.json()
    if (response.ok) {
        window.location.reload()
    } else {
        alert(response_json['message'])
    }
}

let origin_review = '';

async function changePatchInput(review_id) {
    let review = document.getElementById(`review_${review_id}`)
    let patch_btn = document.getElementById(`patch_btn_${review_id}`)
    let delete_btn = document.getElementById(`delete_btn_${review_id}`)
    console.log(origin_review)
    if (patch_btn.innerText === '수정') {
        let inputElement = document.createElement("input");
        if (origin_review === '') {
            origin_review = review.innerText
        }
        inputElement.type = "text";
        inputElement.id = `review_${review_id}`;
        inputElement.className = 'review-content';
        inputElement.placeholder = review.innerText;

        review.parentNode.replaceChild(inputElement, review);
        loadReviews()

        patch_btn.innerText = '취소'
        delete_btn.innerText = '완료'
        delete_btn.onclick = function () {
            patchReview(review_id)
        }
    } else {
        let pElement = document.createElement("p");
        pElement.id = `review_${review_id}`;
        pElement.className = `review-content`;
        pElement.innerText = `${origin_review}`;
        console.log(407, review_id)
        console.log(408, pElement)
        review.parentNode.replaceChild(pElement, review);

        loadReviews()
        patch_btn.innerText = '수정'
        delete_btn.innerText = '삭제'
        delete_btn.onclick = function () {
            deleteReview(review_id)
        }
    }
}


async function patchReview(review_id) {
    let review = document.getElementById(`review_${review_id}`).value
    if (review.length < 10) {
        alert('리뷰는 최소 10자 이상 부터 수정 가능합니다.')
        return false
    }
    console.log(JSON.stringify({"review": review}))
    const response = await fetch(`${backend_base_url}/store/review/${review_id}`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${access_token}`,
        },
        body: JSON.stringify({"review": review}),
        method: 'PATCH',
    });
    let response_json = await response.json()
    if (response.ok) {
        window.location.reload()
    } else {
        alert(response_json['message'])
    }
}