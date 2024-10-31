const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값

window.onload = async function () {
    const parts = window.location.href.split('/');
    const nonEmptyParts = parts.filter(part => part.length > 0);
    const goodsId = nonEmptyParts[nonEmptyParts.length - 1];
    document.getElementById('review_save_btn').onclick = function () {
        createReview(goodsId)
    }
    const response = await fetch(`${backend_base_url}/store/review/${goodsId}`, {
        headers: {
            'content-type': 'application/json',
            "Authorization": `Bearer ${access_token}`,
        },
        method: 'GET',
    });
    if (response.ok) {
        let response_json = await response.json()
        // 리뷰 평균 및 총점
        let avg = 0;
        let total = `리뷰(${response_json.length})`;
        $('#review_total').append(total);

        // 리뷰 리스트
        $('#review_list').empty();
        await response_json.forEach((data) => {
            let review = data['review'];
            let nickname = data['nickname'];
            let profile_image = data['profile_image'];
            let star = data['star'];
            let created_at = data['created_at'];
            let temp_html = `
                                    <h5>이미지 : ${profile_image}</h5>
                                    <h5>닉네임 : ${nickname}</h5>
                                    <h5>리뷰 : ${review}</h5>
                                    <h5>별점 : ${star}</h5>
                                    <h5>작성일 : ${created_at}</h5>
                                    <hr>
                                    `;
            $('#review_list').append(temp_html);
            avg += star * 1  //형변환
        });
        $('#review_avg').append(avg);
    }
    ;
};

async function createReview(goodsId) {
    if (access_token) {
        let review = document.getElementById("review_area").value
        let star = getSelectedStarRating()
        if (review === '' || !star) {
            document.getElementById('error_msg').innerText = '필수사항을 모두 채워주세요.'
            document.getElementById('error_msg').style.display = 'block'
            return
        }
        let data = {
            "review": review,
            "star": star
        }
        console.log(data)
        const response = await fetch(`${backend_base_url}/store/review/${goodsId}`, {
            headers: {
                'content-type': 'application/json',
                "Authorization": `Bearer ${access_token}`,
            },
            body: JSON.stringify(data),
            method: 'POST',
        });
        data = await response.json()
        if (response.ok) {
            window.location.href=`/store/goods/detail/${goodsId}`
        } else {
            if (data.message) {
                document.getElementById('error_msg').innerText = data.message
                document.getElementById('error_msg').style.display = 'block'
            } else if (data['non_field_errors']) {
                document.getElementById('error_msg').innerText = data['non_field_errors'][0]
                document.getElementById('error_msg').style.display = 'block'
            }
        }
    }
};