function validar_formulario() {

		var username = document.formRegistro.username;
		var email = document.formRegistro.correo;
		var password = document.formRegistro.password;
		var formato_email="//w-";
		if (email.value.match(formato_email)) {
			alert("El campo correo no puede ser blanco");
			email.focus();
			return false;
		}	
		
		var username_len = username.value.length;
		if (username_len==0  || username_len<8 ) {
			alert("Debes ingresar un Usuario con minimo 8 caracteres");
			username_len.focus();
			return false;
		}

		var passid_len=password.value.length;
		if (passid_len==0 || passid_len<8 ) {
			alert("Debes ingresar una contraseña con minimo 8 caracteres");
			passid_len.focus();
			return false;
		}
	}

function mostrarContraseña() {
	document.formRegistro.password.setAttribute("type")
}

function ocultarContraseña() {
	var tipo=document.getElementById("password");
	if (tipo.type=="text") {
		tipo.type="password";
	}

}