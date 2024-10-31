const access_token = localStorage.getItem('access_token')

window.onload = async function () {
    const response = await fetch(`${backend_base_url}/store/order`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${access_token}`,
        },
        method: 'GET',
    });
    let response_json = await response.json()
    $('#order_list').empty();
    if (response_json.length === 0) {
        let temp_html = `     
                        지난 주문 내역이 없어요
                    `
        $('#order_list').append(temp_html);
    } else {
        await response_json.forEach((response_json) => {
            let id = response_json['id']
            let category = response_json['category'];
            let image = response_json['image'];
            if (!image) {
                image = staticPath + 'thum.png';
            }
            let name = response_json['name'];
            let price = response_json['format_price'];
            let store_address = response_json['store_address'];
            let review_total = response_json['review_total'];
            let star_avg = response_json['star_avg'];
            star_avg = star_avg / 5 * 100
            if (star_avg === 0) {
                star_avg = 100
            }
            let temp_html = `
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
                                    `;
            $('#order_list').append(temp_html);
        });
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
    if (blockCount >= 4) {
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
