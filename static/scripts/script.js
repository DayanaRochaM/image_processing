$(function() { //shorthand document.ready function
    
    // Para pegar as alterações no arquivo a ser submetidas
	var form;
	$('#file').change(function (event) {
    	form = new FormData();
    	form.append('file', event.target.files[0]); 
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
    	      	document.getElementById('imageid').src = "static/images/original/image.png?" + new Date().getTime();
        	    document.getElementById('undo').disabled = true;
            },
        	error: function (request, status, erro) {
                alert("Problema ocorrido: " + status + "\nDescição: " + erro);
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
        formFilter.append('filter', this.id); 

        $.ajax({
            type: "POST",
            url: "/apply_filter",
            data: formFilter,
            processData: false,
                contentType: false,
            success: function() {
                //display message back to user here
                document.getElementById('imageid').src = "static/images/original/image.png?" + new Date().getTime();
                $("#undo").removeAttr('disabled');
            },
            error: function (request, status, erro) {
                alert("Problema ocorrido: " + status + "\nDescição: " + erro);
                //Abaixo está listando os header do conteudo que você requisitou, só para confirmar se você setou os header e dataType corretos
                //alert("Informações da requisição: \n" + request.getAllResponseHeaders());
            }
        });
    });
});
