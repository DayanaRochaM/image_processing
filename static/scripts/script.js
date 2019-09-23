$(function() { //shorthand document.ready function
    
    // Variaveis usadas
    var name_file, list, extension, form, p1x, p1y, p2x, p2y;
    var extension_aus = "jpeg", graph_width, graph_height;
    // Suporte para filtro de dois pontos
    var graph = document.getElementById("myGraph");
    var graph_point0 = graph.getContext("2d");
    var graph_point1 = graph.getContext("2d");
    var graph_point2 = graph.getContext("2d");

    function tryLoadImage(){
        if (extension == "jpg"){
            extension = "jpeg";
        }
        if (extension == "tif"){
            extension = "png";
        }
        document.getElementById('imageid').src = "static/images/actual/image.".concat(extension).concat("?") + new Date().getTime();
    }

    function replotGraph(){
        $('#divGraph').removeChild(graph);
        $('#divGraph').append('<canvas id="myGraph" width="150" height="150"></canvas>');
        graph = document.getElementById("myGraph");
        graph_point0 = graph.getContext("2d");
        graph_point1 = graph.getContext("2d");
        graph_point2 = graph.getContext("2d");
        initializateGraph();
    }

    function initializateGraph(){

        graph_point0.moveTo(0, graph_height);
        graph_point0.lineTo(p1x, p1y);
        graph_point0.stroke();

        graph_point1.moveTo(p1x, p1y);
        graph_point1.lineTo(p2x, p2y);
        graph_point1.stroke();

        graph_point2.moveTo(p2x, p2y);
        graph_point2.lineTo(graph_width, 0);
        graph_point2.stroke();
    }

    function getCorrespondent(value, scale){
        var result = value*255/scale;
        return result;
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

    // Pegar alterações de dois pontos
    $('#two_points-p1x').change(function (event) {
        replotGraph();
        var p1x = $(this).val();
        p1x = getCorrespondent(p1x, graph_width);
        graph_point0.lineTo(p1x, p1y);
        graph_point1.moveTo(p1x, p1y);
        graph_point0.stroke();
        graph_point1.stroke();
    });
    $('#two_points-p1y').change(function (event) {
        replotGraph();
        var p1y = $(this).val();
        p1y = getCorrespondent(p1y, graph_height);
        graph_point0.lineTo(p1x, p1y);
        graph_point1.moveTo(p1x, p1y);
        graph_point0.stroke();
        graph_point1.stroke();
    });
    $('#two_points-p2x').change(function (event) {
        replotGraph();
        var p2x = $(this).val();
        p2x = getCorrespondent(p2x, graph_width);
        graph_point1.lineTo(p2x, p2y);
        graph_point2.moveTo(p2x, p2y);
        graph_point1.stroke();
        graph_point2.stroke();
    });
    $('#two_points-p2y').change(function (event) {
        replotGraph();
        var p2y = $(this).val();
        p2y = getCorrespondent(p2y, graph_height);
        graph_point1.lineTo(p2x, p2y);
        graph_point2.moveTo(p2x, p2y);
        graph_point1.stroke();
        graph_point2.stroke();
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

                // Configurando gráfico
                graph_width = graph.width; 
                graph_height = graph.height;
                p1x = 50;
                p1y = graph_height-50;
                p2x = 70;
                p2y = graph_height-70;
                initializateGraph(graph_width, graph_height);
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

        if (id === 'gaussian' || id === 'laplacian'){
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
