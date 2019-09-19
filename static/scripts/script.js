$(function() { //shorthand document.ready function
    
    // Variaveis usadas
    var name_file;
    var list;
    var extension; // Extensão da imagem
    var extension_aus = "jpeg";

    function tryLoadImage(){
        if (extension == "jpg"){
            extension = "jpeg";
        }
        document.getElementById('imageid').src = "static/images/actual/image.".concat(extension).concat("?") + new Date().getTime();
    }

    // Para pegar as alterações no arquivo a ser submetidas
	var form;
	$('#file').change(function (event) {
    	form = new FormData();
    	form.append('file', event.target.files[0]); 
        name_file = event.target.files[0].name;
        list = name_file.split(".");
        extension = list[list.length-1];
	});

	$("#submit").click(function() {
        $.ajax({
        	type: "POST",
        	url: "/upload_image",
        	data: form,
        	processData: false,
            	contentType: false,
        	success: function() {
    	      	//display message back to user here
                tryLoadImage();
                $('.filter').attr('disabled', false);
                $('.filter-with-text').attr('disabled', false);
                $('.non-filter').attr('disabled', true);
                $('#calc-histogram').attr('disabled', false);
            },
        	error: function (request, status, erro) {
                alert("Problema ocorrido: " + status + "\nDescição: " + erro);
                $('.filter').attr('disabled', true);
                $('.filter-with-text').attr('disabled', true);
                //Abaixo está listando os header do conteudo que você requisitou, só para confirmar se você setou os header e dataType corretos
                //alert("Informações da requisição: \n" + request.getAllResponseHeaders());
            }
        });
        return false;
	});

    // Para aplicar filtros. O controle é feito com o id do botão.
    // Todo filtro terá um botão com o nome do filtro por ele aplicado. 
    $(".filter").click(function() {
        var formFilter = new FormData();
        var id = this.id;
        formFilter.append('filter', id); 

        $.ajax({
            type: "POST",
            url: "/apply_filter",
            data: formFilter,
            processData: false,
                contentType: false,
            success: function() {
                //display message back to user here
                tryLoadImage();
                $('#'.concat(id)).attr('disabled', true);
                $('#'.concat('non-',id)).attr('disabled', false);
            },
            error: function (request, status, erro) {
                alert("Problema ocorrido: " + status + "\nDescição: " + erro);
                //Abaixo está listando os header do conteudo que você requisitou, só para confirmar se você setou os header e dataType corretos
                //alert("Informações da requisição: \n" + request.getAllResponseHeaders());
            }
        });
    });

    $(".filter-with-text").click(function() {
        var formFilter = new FormData();
        var id = this.id;
        formFilter.append('filter', id); 

        if (id === 'gaussian'){
            formFilter.append('n', $("#".concat(id,"-n")).val());
            formFilter.append('sigma', $("#".concat(id,"-sigma")).val());
        }
        else {
            formFilter.append('text', $("#".concat(id,"-text")).val());
        }

        $.ajax({
            type: "POST",
            url: "/apply_filter",
            data: formFilter,
            processData: false,
                contentType: false,
            success: function() {
                //display message back to user here
                tryLoadImage();
                $('#'.concat(id)).attr('disabled', true);
                $('#'.concat('non-',id)).attr('disabled', false);
            },
            error: function (request, status, erro) {
                alert("Problema ocorrido: " + status + "\nDescição: " + erro);
                //Abaixo está listando os header do conteudo que você requisitou, só para confirmar se você setou os header e dataType corretos
                //alert("Informações da requisição: \n" + request.getAllResponseHeaders());
            }
        });
    });

    // Para retirar filtros. O controle é feito com o id do botão.
    $(".non-filter").click(function() {
        var formFilter = new FormData();
        var id = this.id;
        formFilter.append('filter', this.id); 

        $.ajax({
            type: "POST",
            url: "/apply_filter",
            data: formFilter,
            processData: false,
                contentType: false,
            success: function() {
                //display message back to user here
                tryLoadImage();
                $('#'.concat(id)).attr('disabled', true);
                $('#'.concat(id.slice(4))).attr('disabled', false);
            },
            error: function (request, status, erro) {
                alert("Problema ocorrido: " + status + "\nDescição: " + erro);
                //Abaixo está listando os header do conteudo que você requisitou, só para confirmar se você setou os header e dataType corretos
                //alert("Informações da requisição: \n" + request.getAllResponseHeaders());
            }
        });
    });


    // Para calcular e exibir histograma da imagem
    $("#calc-histogram").click(function() {
        // var formFilter = new FormData();
        // var id = this.id;
        // formFilter.append('filter', id); 

        $.ajax({
            type: "GET",
            url: "/show_histogram",
            //data: formFilter,
            processData: false,
                contentType: false,
            success: function() {
                //display message back to user here
                document.getElementById('image-histogram').src = "static/images/histogram/hist-image.png?" + new Date().getTime();
                //$('#'.concat(id)).attr('disabled', true);
                //$('#'.concat('non-',id)).attr('disabled', false);
            },
            error: function (request, status, erro) {
                alert("Problema ocorrido: " + status + "\nDescição: " + erro);
                //Abaixo está listando os header do conteudo que você requisitou, só para confirmar se você setou os header e dataType corretos
                //alert("Informações da requisição: \n" + request.getAllResponseHeaders());
            }
        });
    });

});
