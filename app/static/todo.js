window.onload = function () {

    const editable = $(".heading, .notes")

    function addFocusIn(el) {
        let element = $(el)
        element.data("currentText", element.text())
    }

    function addFocusOut(el) {
        let element = $(el)
        if (element.data("currentText") !== element.text())
            element.trigger("change")
    }

    editable.on("focusin", function () {
        addFocusIn(this)
    })

    editable.on("focusout", function () {
        addFocusOut(this)
    })

    $(".feed-item img").on("click", function () {
        let id = $(this).closest(".feed-item").attr("todo-id");
        let src = this.src;
        if (src.endsWith("heart.png")) {
            return window.location.replace(`/todo/${id}/like`)
        }
        window.location.replace(`/todo/${id}/unlike`)
    })

    $(".todo-item .button4").on("click", function () {
        let id = $(this).closest(".todo-item").attr("todo-id");
        if (confirm("Are you sure you want to delete this todo?")) {
            window.location.replace(`/todo/${id}/delete`)
        }
    })

    $(".todo-item .checkbox").on("click", function () {
        let id = $(this).closest(".todo-item").attr("todo-id");
        if (confirm("Are you sure you want to mark this todo as completed?")) {
            window.location.replace(`/todo/${id}/complete`)
        }
    })

    $(".todo-item .heading").on("change", function () {
        let id = $(this).closest(".todo-item").attr("todo-id");
        let title = this.innerText;
        let formData = new FormData();
        formData.append("title", title);
        pushUpdate(formData, id);
    })


    $(".todo-item .notes").on("change", function () {
        let id = $(this).closest(".todo-item").attr("todo-id");
        let description = this.innerText;
        let formData = new FormData();
        formData.append("description", description);
        pushUpdate(formData, id);
    })

    function pushUpdate(formData, id) {
        $.ajax({
            url: `/todo/${id}/edit`,
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                let data = JSON.parse(response);
                if (data.result !== "success")
                    return alert("An error occurred while trying to update your todo.")
            }
        })
    }

}
