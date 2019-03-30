/*Mensagens de Erro*/
const MSG_VARIAVEL_DATE = 'Não foi encontrada a variável "date" no dataset';
const MSG_VARIAVEL_GERAL = 'Por padrão, algumas nomes de variáveis são esperados ' 
							+  'para definir elementos do gráfico';

/*
Criando valores de default para gráficos.
Aqui são definidos os valores 
*/
var margin = {top: 20, right: 20, bottom: 20, left: 30};
var width = svgDims.width - margin.left - margin.right;
var height = svgDims.height - margin.top - margin.bottom;

function checkVariavelEsperada(variaveis, variavelEsperada){
	/*
	Verifica se existe se um nome de variável esperado existe
	--variaveis: array com nomes das variáveis
	--variavelEsperada: variável a ser verificada

	--return: True of False
	*/
	
	/*encontrar variável no array*/
	for( i = 0; i < variaveis.length; i++){
		if( variaveis[ i ] == variavelEsperada ){
			return 1;
		};
	};

	debugger;

	alert(MSG_VARIAVEL_DATE + '\n' + MSG_VARIAVEL_GERAL);

	return 0;
};

function drawTimeSeries( raw_data, svgDims ){
	/*
	Desenha um grafico temporal
	raw_data deve possuir uma variável chamada "date" para criacao do eixo 
		horizontal
	*/

	/*verififcar se existe a variável dentro do dataset -- case sensitive*/
	if( checkVariavelEsperada( Object.keys( raw_data[0] ), 'date' ) == 0 ){	
		return 0;
	};

};