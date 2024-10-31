const access_token = localStorage.getItem('access_token')  //Token value required when requesting
let lastClickedDt = null; // save modal selected element

window.onload = async function () {
    let storeId = localStorage.getItem('store_id')
    if (!storeId) {
        alert('Available only to sellers.')
        window.location.href = '/store/goods/list'
    }
    const response = await fetch(`${backend_base_url}/store/${storeId}`, {
        headers: {
            'content-type': 'application/json', "Authorization": `Bearer ${access_token}`,
        }, method: 'GET',
    });
    let response_json = await response.json()
    let registrationPath = staticPath + 'icon/registration.svg';
    if (response.ok) {
        if (response_json['goods_set'].length === 0) {
            document.getElementById('admin_goods_empty').style.display = 'block';
            document.getElementById('admin_goods_btn').className = 'btn on';
            document.getElementById('admin_goods_btn').innerText = 'registration';
        } else {
            response_json['goods_set'].forEach((data) => {
                let name = data['name']
                let category = data['category']
                let description = data['description']
                let price = data['format_price']
                let image = data['image_set'][0]
                let order_set = data['order_set']
                let review_set = data['review_set']
                if (!image) {
                    image = staticPath + 'thum.png';
                }
                let star_avg = data['star_avg'];  // Adjust the number of icons later
                star_avg = star_avg / 5 * 100
                if (star_avg === 0) {
                    star_avg = 100
                }
                let temp_html = `
                        <li id="goods_${data['goods_id']}" class="goods-card">
                            <div class="admin_thum">
                                <img src="${image}"
                                     alt=""/>
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
                                <p class="description goods_description" >${description}</p>
                            </div>
                        </li>
                `

                $('#admin_goods_list').append(temp_html);

                // Order Category Settings -> Should I also add those without orders?
                let order_goods_select_html2 = `
                        <li value="goods_id_${data['goods_id']}">${name}</li>
                `;
                $('.order_goods_select').append(order_goods_select_html2);
                $('.order_goods_select').on('click', 'li', function () {
                    var selectedValue = $(this).attr('value');
                    var change_filter = $(this).text();
                    document.getElementById('textToShow').innerText = change_filter;
                    filterOrderList(selectedValue);
                });

                // Review category settings -> Should I add those without reviews as well?
                let review_goods_select_html2 = `
                        <li value="reveiw_goods_id_${data['goods_id']}">${name}</li>
                `;
                $('.review_goods_select').append(review_goods_select_html2);
                $('.review_goods_select').on('click', 'li', function () {
                    var selectedValue2 = $(this).attr('value');
                    var change_filter2 = $(this).text();
                    document.getElementById('textToShow2').innerText = change_filter2;
                    filterReviewList(selectedValue2)
                    const moreButton = document.getElementById("moreButton");
                    // moreButton.style.display = "block";
                    // removeMoreButtons()
                    // test()
                    updateMoreButton()
                });

                // Load order list
                orderList(order_set);

                // Load review list
                reviewList(review_set, image);
            });

            let temp_html2 = `
                            <li onclick="addGoodsCard()" id="add_goods" style="display:none;">
                                <div class="plus">
                                    <img src="${registrationPath}" alt=""/>
                                </div>
                            </li>
            `
            $('#admin_goods_list').append(temp_html2);

            document.getElementById('admin_goods_btn').className = 'btn on';
            document.getElementById('admin_goods_btn').innerText = 'correction';

            // To edit card when clicking button
            await changeGoodsCard()
        }
    }

};


async function changeGoodsCard() {
    // Add event when clicking edit button
    $('#admin_goods_btn').click(function () {
        // Select all cards on the page
        $('.goods-card').each(function () {
            // Get data for current card
            let goodsId = $(this).attr('id').split('_')[1];
            let name = $(this).find('.name').text();
            let category = $(this).find('.category').text();
            let price = $(this).find('.cost').text();
            price = price.replace(/,/g, '').replace('Kip', '');
            let description = $(this).find('.goods_description').text();
            let image = $(this).find('img').attr('src');

            // Updated with new card structure
            let temp_html = `
                    <li class="origin_goods" id="goods_${goodsId}">
                        <div class="thum">
                            <input id="goods_image_${goodsId}" class="file origin_card_input" type="file" multiple accept=".jpg, .png, .jpeg"/>
                            <label class="label" for="goods_image_${goodsId}" style="background: url(${image});" ></label>
                        </div>
                        <div class="info">
                            <dl class="goods_name">
                                <dt>${name}</dt>
                                <dd>
                                    <button class="modal-button">input</button>
                                </dd>
                            </dl>
                            <dl class="goods_category">
                                <dt>${category}</dt>
                                <dd>
                                    <button class="modal-button">input</button>
                                </dd>
                            </dl>
                            <dl class="goods_price">
                                <dt>${price}</dt>
                                <dd>
                                    <button class="modal-button">input</button>
                                </dd>
                            </dl>
                            <dl class="goods_description">
                                <dt>${description}</dt>
                                <dd>
                                    <button class="modal-button">input</button>
                                </dd>
                            </dl>
                            <dl class="goods_delete" style="justify-content: center;">
                                <dt onclick="creatDeleteModal(${goodsId})">delete</dt>
                            </dl>
                        </div>
                    </li>
                `

            $(this).replaceWith(temp_html);
            creatModal();
            // Code added to the background when adding an image
            $('.file').change(function () {
                updateLabelBackground(this); // Call a function when a file changes
            });
            fileLoadImage('origin')
        });
    });

}

async function creatModal() {
    // $('#admin_goods_list').append(temp_html);
    // Add event listeners to all "input" buttons
    const closeModal = document.getElementById("close-modal");
    const modal = document.querySelector(".modal-wrapper");
    $('.modal-button').on('click', function () {
        document.getElementById('goods_input').style.display = 'block'

        let dlClass = $(this).closest('dl').attr('class'); // Class value of dl to which the current button belongs
        lastClickedDt = $(this).closest('dl').find('dt')[0];
        if (dlClass === 'goods_name') {
            document.getElementById('modal_title').innerHTML = 'of the selected product <br>' + '<span>product name</span>Please enter';
            document.getElementById('input_goods_info').placeholder = 'Enter product name';
        } else if (dlClass === 'goods_category') {
            document.getElementById('modal_title').innerHTML = 'of the selected product  <br>' + '<span>category</span>Please enter';
            document.getElementById('input_goods_info').placeholder = 'Enter category';
        } else if (dlClass === 'goods_price') {
            document.getElementById('modal_title').innerHTML = 'of the selected product  <br>' + '<span>price</span>Please enter';
            document.getElementById('input_goods_info').placeholder = 'Enter price';
            document.getElementById('input_goods_info').type = 'number';
        } else if (dlClass === 'goods_description') {
            document.getElementById('modal_title').innerHTML = 'of the selected product <br>' + '<span>Product Description</span>Please enter';
            let inputElement = document.getElementById('input_goods_info');
            let textareaElement = document.createElement('input');

            // If necessary, copy the input element's properties.
            textareaElement.value = inputElement.value;
            textareaElement.placeholder = 'Product Description';
            textareaElement.id = inputElement.id;
            textareaElement.name = inputElement.name;

            inputElement.parentNode.replaceChild(textareaElement, inputElement);

        }
        document.getElementById('save_modal').onclick = function () {
            changeGoodsInfo();
        };
        modal.style.display = "flex"; // modal display
    });


    closeModal.onclick = () => {
        modal.style.display = "none";
        let originElement = document.getElementById('input_goods_info');
        let inputElement = document.createElement('input');

        // Convert to input tag
        inputElement.value = '';
        inputElement.id = originElement.id;
        inputElement.name = originElement.name;

        originElement.parentNode.replaceChild(inputElement, originElement);

    };
}

async function addGoodsCard() {
    let registrationPath = staticPath + 'icon/registration.svg';
    let temp_html = `
                            <li class="new_goods">
                                <div class="thum">
                                    <label class="label new_card_label">
                                        <input class="file new_card_file" type="file"  multiple accept=".jpg, .png, .jpeg"/>
                                    </label>
                                </div>
                                <div class="info">
                                    <dl class="goods_name">
                                        <dt>product name</dt>
                                        <dd>
                                            <button class="modal-button">input</button>
                                        </dd>
                                    </dl>
                                    <dl class="goods_category">
                                        <dt>category</dt>
                                        <dd>
                                            <button class="modal-button">input</button>
                                        </dd>
                                    </dl>
                                    <dl class="goods_price">
                                        <dt>price</dt>
                                        <dd>
                                            <button class="modal-button">input</button>
                                        </dd>
                                    </dl>
                                    <dl class="goods_description">
                                        <dt>Product Description</dt>
                                        <dd>
                                            <button class="modal-button">input</button>
                                        </dd>
                                    </dl>
                                   <dl className="goods_delete"  style="justify-content: center;">
                                        <dt onClick="deleteCard(event)">delete</dt>
                                    </dl>
                                </div>
                            </li>
                `
    $('#admin_goods_list').append(temp_html);

    $('#add_goods').remove();
    let temp_html2 = `
                            <li onclick="addGoodsCard()" id="add_goods" style="display:block;">
                                <div class="plus">
                                    <img src="${registrationPath}" alt=""/>
                                </div>
                            </li>
            `
    $('#admin_goods_list').append(temp_html2);
    // modal
    await creatModal()
    // Code added to the background when adding an image
    $('.file').change(function () {
        updateLabelBackground(this); // Call a function when a file changes
    });

    await fileLoadImage('new')
}

function fileLoadImage(category) {
    if (category === 'new') {
        document.querySelectorAll('.file.new_card_file').forEach(function (fileInput) {
            fileInput.addEventListener('change', function (event) {
                const label = event.target.closest('.label');
                console.log(293)
                if (label) {
                    label.classList.add('background-cover');
                }
            });
        });
    } else if (category === 'origin') {
        document.querySelectorAll('.file.origin_card_input').forEach(function (fileInput) {
            fileInput.addEventListener('change', function (event) {
                console.log(301)
                const label = event.target.closest('.label');
                if (label) {
                    label.classList.add('background-cover');
                }
            });
        });
    }

}


async function changeBtn(category = null) {
    let btn = document.getElementById('admin_goods_btn');
    if (category === 1) {
        btn.style.display = 'block';
        return
    } else if (category === 2) {
        btn.style.display = 'none';
        document.getElementById('tab03').style.display = 'block';
        filterOrderList('0')
        return
    }
    let empty_icon = document.getElementById('admin_goods_empty');
    let empty_icon2 = document.getElementById('admin_goods_empty_2');
    let goods_list = document.getElementById('admin_goods_list');
    let add_goods = document.getElementById('add_goods');
    let origin_goods = document.querySelector('.origin_goods');
    let new_goods = document.querySelector('.new_goods');
    if (btn.innerText === 'registration' | btn.innerText === 'correction') {

        btn.innerText = 'complete';
        btn.className = 'btn complete';
        if (goods_list.innerText) {
            empty_icon2.style.display = 'none';
            empty_icon.style.display = 'none';
            add_goods.style.display = 'block';
            return
        }
        if (empty_icon.style.display === 'block') {
            empty_icon2.style.display = 'block';
            empty_icon.style.display = 'none';
        }

    } else if (btn.innerText === 'complete' || btn.innerText === '') {
        if (goods_list.innerText) {
            let _confirm = confirm('When editing an image, all images of existing products will be deleted.\nDo you want to edit?')
            if (!_confirm) {
                return false
            }
            let create_goods = await createGoodsInfo()
            if (create_goods === false) {
                return
            } else {
                await patchGoodsInfo()
                window.location.reload()
            }
            btn.className = 'btn on';
            btn.innerText = 'correction';
            empty_icon2.style.display = 'none';
            empty_icon.style.display = 'none';
            add_goods.style.display = 'none';
            return
        }
        if (empty_icon.style.display === 'none') {
            btn.innerText = 'registration';
            empty_icon2.style.display = 'none';
            empty_icon.style.display = 'block';
            await createGoodsInfo()
        }
    }
}


async function changeGoodsInfo() {
    const modal = document.querySelector(".modal-wrapper");
    let data = document.getElementById('input_goods_info');
    let inputElement = document.createElement('input');
    // Set data on last clicked "Enter" button
    if (lastClickedDt) {
        // $(lastClickedDt).innerText = data; // Here we set the data as the text of the button.
        $(lastClickedDt).text(data.value);
    }

    // Hide modal
    modal.style.display = "none";

    // Convert to input tag
    inputElement.value = '';
    inputElement.id = data.id;
    inputElement.name = data.name;

    data.parentNode.replaceChild(inputElement, data);
}


async function patchGoodsInfo() {
    let goods_set = [];

    // Promise array to contain processing for all products
    let promises = $('.origin_goods').map(async function () {
        let currentElement = $(this);
        let goods_id = currentElement.closest('li').attr('id').split('_')[1];

        // You can select multiple images at once -> I think you need to add some text
         // When editing an image, all existing images are deleted and filled with new photos.
        let imageFiles = document.getElementById(`goods_image_${goods_id}`).files
        let imagePromises = Array.from(imageFiles).map(file => convertToBase64(file));
        let imageSet = await Promise.all(imagePromises);
        let goodsInfo = {
            id: goods_id,
            category: currentElement.find('.goods_category dt').text(),
            name: currentElement.find('.goods_name dt').text(),
            price: currentElement.find('.goods_price dt').text(),
            description: currentElement.find('.goods_description dt').text(),
            images: imageSet
        };

        return goodsInfo;
    }).get();

    goods_set = await Promise.all(promises);

    // send to server
    const response = await fetch(`${backend_base_url}/store/goods`, {
        method: 'PATCH', headers: {
            "Authorization": `Bearer ${access_token}`, "Content-Type": "application/json"
        }, body: JSON.stringify({goods_set})
    });

}


async function createGoodsInfo() {
    let goods_set = [];
    // Promise array to contain processing for all products
    let new_goods = document.querySelector('.new_goods');
    let promises = $('.new_goods').map(async function () {
        let currentElement = $(this);

        // You can select multiple images at once -> I think you need to add some text
         // When editing an image, all existing images are deleted and filled with new photos.
        let imageFiles = currentElement.find('.file')[0].files
        let imagePromises = Array.from(imageFiles).map(file => convertToBase64(file));
        let imageSet = await Promise.all(imagePromises);
        let goodsInfo = {
            category: currentElement.find('.goods_category dt').text(),
            name: currentElement.find('.goods_name dt').text(),
            price: currentElement.find('.goods_price dt').text(),
            description: currentElement.find('.goods_description dt').text(),
            images: imageSet
        };

        if (goodsInfo.category === '' || goodsInfo.name === '' || goodsInfo.price === '' || goodsInfo.images.length === 0 || goodsInfo.category === 'category' || goodsInfo.name === 'product name' || goodsInfo.price === 'price') {
            document.getElementById('error_msg').innerText = 'Please fill out all required elements (image, product name, category, price)'
            document.getElementById('error_msg').style.display = 'block'
            return false
        }

        return goodsInfo;
    }).get();

    goods_set = await Promise.all(promises);
    if (!goods_set[0] && new_goods) {
        return false
    }
    if (goods_set.length !== 0) {
        let store_id = localStorage.getItem('store_id')
        // send to server
        const response = await fetch(`${backend_base_url}/store/${store_id}`, {
            method: 'POST', headers: {
                "Authorization": `Bearer ${access_token}`, "Content-Type": "application/json"
            }, body: JSON.stringify({goods_set})
        });

    }
}


// Convert image to base64
function convertToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function updateLabelBackground(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            // Set the background image of the label associated with the input
            if ($(input).closest('.label').length === 0) {
                $(input).next('label').css('background', 'url(' + e.target.result + ')');
            } else {
                $(input).closest('.label').css('background', 'url(' + e.target.result + ')');
            }
        };

        reader.readAsDataURL(input.files[0]); // Start reading file
    }
}


async function orderList(order_set) {
    order_set.forEach((data) => {
        let goods_id = data['goods']
        let user_name = data['user_name']
        let goods_name = data['goods_name']
        let ordered_at = data['ordered_at']
        let temp_html = `
        <li class="goods_id_${goods_id}">
            <div>
                <span class="name">'${user_name}'</span>is
                <span class="product">${goods_name}</span> the product
                I ordered it.
            </div>
            <span class="day">${ordered_at}</span>
        </li>
`
        $('#order_list').append(temp_html)
    })
}

function filterOrderList(selectedValue) {
    $("#order_list li").css("display", "none");

    if (selectedValue === '0') {
        $("#order_list li").css("display", "block");

    } else {
        $("#order_list li." + selectedValue).css("display", "block");
    }
}


function reviewList(review_set, image) {
    review_set.forEach((data) => {
        let goods_id = data['goods_id']
        let created_at = data['created_at']
        let user_name = data['user_name']
        let review = data['review']
        let star = data['star']
        let user_profile = data['user_profile']
        star = star / 5 * 100
        let temp_html = ''
        if (user_profile !== 'false' && user_profile !== null) {
            temp_html = `
                <li class="reveiw_goods_id_${goods_id} review-box">
                    <div class="thum" style="background: url(${image}); background-size: cover;">
                    </div>
                    <div class="info">
                        <div class="flex">
                            <div class="user">
                                <div class="img">
                                    <img class="review_img" src="${user_profile}" alt=""/>
                                </div>
                                <div class="txt">
                                    ${user_name}
                                    <div class="star">
                                        <div class="on" style="width: ${star}%"></div>
                                    </div>
                                </div>
                            </div>
                            <span class="day">${created_at}</span>
                        </div>
                        <p class="review-content">${review}</p>
                    </div>
                </li>
            `
        } else {
            user_profile = staticPath + 'icon/profile.svg'
            temp_html = `
                <li class="reveiw_goods_id_${goods_id} review-box">
                    <div class="thum" style="background: url(${image}); background-size: cover;">
                    
                    </div>
                    <div class="info">
                        <div class="flex">
                            <div class="user">
                                <div class="img empty02">
                                    <img src="${user_profile}" alt=""/>
                                </div>
                                <div class="txt">
                                    ${user_name}
                                    <div class="star">
                                        <div class="on" style="width: ${star}%"></div>
                                    </div>
                                </div>
                            </div>
                            <span class="day">${created_at}</span>
                        </div>
                        <p class="review-content">${review}</p>
                    </div>
                </li>
            `
        }

        $('#review_list').append(temp_html)
    })
    filterReviewList('0'); // Update 'See More' button status
}

function updateMoreButton() {
    const moreButton = document.getElementById("moreButton");
    let currentIndex = 8;

    // If the number of filtered reviews is 8 or less, the 'See more' button is hidden.
    if (currentFilteredReviews.length <= 8) {
        moreButton.style.display = "none";
    } else {
        moreButton.style.display = "block";

        moreButton.onclick = function () {
            let maxIndex = Math.min(currentIndex + 8, currentFilteredReviews.length);
            for (let i = currentIndex; i < maxIndex; i++) {
                currentFilteredReviews[i].style.display = "flex";
                loadReviews();
            }

            currentIndex += 8;
            if (currentIndex >= currentFilteredReviews.length) {
                moreButton.style.display = "none";
            }
        };
    }
}


let currentFilteredReviews = []; // Array to store currently filtered review items
function filterReviewList(selectedValue) {
    let allReviews = $("#review_list li");
    allReviews.hide(); // Hide all reviews.

    if (selectedValue === '0') {
        currentFilteredReviews = Array.from(allReviews);
    } else {
        currentFilteredReviews = Array.from(allReviews.filter("." + selectedValue));
    }

    currentFilteredReviews.slice(0, 8).forEach(li => li.style.display = 'flex');

    updateMoreButton(); // Update the status of the 'See more' button
    loadReviews();       // add new button
}


async function createFirstGoods() {
    let registrationPath = staticPath + 'icon/registration.svg';
    let empty_icon2 = document.getElementById('admin_goods_empty_2');
    if (empty_icon2.style.display === 'block') {
        empty_icon2.style.display = 'none';
    }
    await addGoodsCard();
}

async function loadReviews() {
    removeMoreButtons()
    let review_active = document.getElementById('reivew_link');
    let style = window.getComputedStyle(review_active);
    let backgroundColor = style.backgroundColor;


    document.getElementById('tab03').style.display = 'block';

    $('.review-box').each(function () {
        var content = $(this).find('.review-content');
        var maxHeight = 60; // set maximum height
        var btn_more = $('<a href="javascript:void(0)" id="more_btn" class="more">...see more</a>');
        $(this).find('.info').append(btn_more);
        if (content[0].offsetHeight > maxHeight) {
            content.css('max-height', maxHeight + 'px');
            content.css('overflow', 'hidden');
        } else {
            btn_more.hide();
        }

        btn_more.click(function () {
            if (content.css('max-height') !== 'none') {
                $(this).html('...fold');
                content.css('max-height', 'none');
            } else {
                $(this).html('...see more');
                content.css('max-height', maxHeight + 'px');
            }
        });
    });

    if (backgroundColor !== 'rgb(255, 79, 22)') {
        document.getElementById('tab03').style.display = 'none';
    }
}

function removeMoreButtons() {
    $('.review-box').each(function () {
        // Find and remove the "See more" button in each review box
        var btn_more = $(this).find('.more');
        if (btn_more.length) {
            btn_more.remove();
        }

        // Reset max-height style for review content
        var content = $(this).find('.review-content');
        content.css('max-height', '');
        content.css('overflow', '');
    });
}


async function creatDeleteModal(goods_id) {
    const modal = document.querySelector(".modal-wrapper");
    document.getElementById('goods_input').style.display = 'none';
    document.getElementById('modal_title').style.display = 'block';
    document.getElementById('modal_title').innerHTML = 'the product <span class="ty03">delete</span>will you do it?\n' +
        '                    <small>Deleted products cannot be restored.</small>';
    document.getElementById('save_modal').style.display = 'block';
    modal.style.display = "flex"; // modal display
    document.getElementById('save_modal').onclick = function () {
        deleteGoods(goods_id);
    };
}

async function deleteGoods(goods_id) {
    alert(goods_id)
    const token = localStorage.getItem('access_token')  //Token value required when requesting
    const response = await fetch(`${backend_base_url}/store/goods`, {
        headers: {
            'content-type': 'application/json', "Authorization": `Bearer ${token}`,
        }, body: JSON.stringify({"goods_id": goods_id}), method: 'DELETE',
    });
    window.location.reload()
}

function deleteCard(event) {
    // Find the parent li element of the element where the event occurred
    let liElement = event.target.closest('li');

    // Remove li element if present
    if (liElement) {
        liElement.remove();
    }
}

