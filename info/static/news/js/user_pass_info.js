function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();

        // TODO 修改密码
        var params = {};
        // 获取到每一个表单中的input  x.name得到input标签中name的值
        $(this).serializeArray().map(function (x) {
            // {old_password: "123456", new_password: "111111", new_password2: "111111"}
            params[x.name] = x.value;
        });
        // 取到两次密码进行判断
        var new_password = params["new_password"];
        var new_password2 = params["new_password2"];

        if (new_password != new_password2) {
            alert('两次密码输入不一致')
            return
        }

        $.ajax({
            url: "/user/user_pass_info",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 修改成功
                    alert("修改成功")
                    window.location.reload()
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})