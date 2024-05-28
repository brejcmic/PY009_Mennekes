// obnovovaci cas hodnot v ms
const PERIODACTENI = 5000

// promenna pro ukladani hodnot prijatych ze serveru
var datavalue = 0;

// =============================================================================
// identifikator diagnostickych zprav
const postmort = document.getElementById("postmort")

// identifikatory registru
{% block register_ids %}{%endblock%}


// =============================================================================
// funkce pro cteni udaju modbus
function ctiModbus() {
		fetch("co.json")
				.then(function(response){
					return response.json()
				})
				.then(function(data){
				    {% block read_coils %}{% endblock %}

				})

		fetch("di.json")
				.then(function(response){
					return response.json()
				})
				.then(function(data){
					{% block read_digital_inputs %}{% endblock %}

				})

		fetch("hr.json")
				.then(function(response){
					return response.json()
				})
				.then(function(data){
					{% block read_holding_registers %}{% endblock %}

				})

		fetch("ir.json")
				.then(function(response){
				 return response.json()
				})
				.then(function(data){
					{% block read_input_registers %}{% endblock %}

				})}

// funkce pro cteni souboru diagnostickych dat
function ctiPostmort() {
	postmort.contentWindow.location.reload();
	postmort.contentWindow.scrollTo( 0, 999999 );
}

// =============================================================================
// cteni stavu modbus
ctiModbus();
// interval obnovovani modbus hodnot
setInterval(ctiModbus, PERIODACTENI);
// interval obnovovani souboru diagnostickych dat
setInterval(ctiPostmort, PERIODACTENI);
