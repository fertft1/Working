/*Mensagens de Erro*/
const MSG_VARIAVEL_SUPERIOR = 'Existem variáveis (colunas) o dataset que não únicas';
const MSG_VARIAVEL_INFERIOR = 'Não foi encontrada a variável especificada para o eixo';
const MSG_VARIAVEL_GERAL = 'A variável a ser utilizada no eixo, deve' 
							+ ' ser especificada';

/*Criando valores de default para gráficos*/
var margin = {top: 20, right: 20, bottom: 30, left: 30};

function checkVariavelEsperada( variaveis, xVar, yVar ){
	/*
	Verifica se existe se um nome de variável esperado existe
	--variaveis: array com nomes das variáveis
	--variavelEsperada: variável a ser verificada
	--return: True of False
	*/
	
	/*encontrar variável no array*/
	var count = 0;
	for( i = 0; i < variaveis.length; i++ ){
		if( variaveis[ i ] === xVar || variaveis[ i ] === yVar ){
			count += 1;
		};
	};

	//verificar se existem inconsistências
	if( count == 2 ){
		return 1;
	}
	else if( count > 2 ){
		alert( MSG_VARIAVEL_SUPERIOR );
		return 0;
	}
	else{
		alert( MSG_VARIAVEL_INFERIOR + '\n' + MSG_VARIAVEL_GERAL );
		return 0;
	};

};

function drawTimeSeries( raw_data, xVar, yVar, element, svgDims ){
	/*
	Desenha um grafico temporal
	raw_data-- dataset
	xVar -- contem o nome da variavel do eixo x
	yVar -- contem o nome da variavel do eixo y
	plot-1 -- espefica o element html onde sera criado o gráfico
	svgDims -- especifica as dimensoes do grafico
	*/

	//região do gráfico
	var width = svgDims.width - margin.left - margin.right;
	var height = svgDims.height - margin.top - margin.bottom;

	/*verificar se existem as variáveis dentro do dataset -- case sensitive*/
	if( checkVariavelEsperada( Object.keys( raw_data[0] ), xVar, yVar ) === 0 ){	
		return 0;
	};

	//criar svg
	var svg = d3.select( "." + element )
				.append( 'svg' )
				.attr( "width", svgDims.width )
				.attr( "height", svgDims.height );

	//criar escalas, ranges e domínios
	var xScale = d3.scaleLinear()
					.range( [ 0, width ] )
					.domain( 
						d3.extent( raw_data, function( d )
							{ return new Date( d[ xVar ] ); } ) );

	var yScale = d3.scaleLinear()
					.range( [ height, 0 ] )
					.domain( 
						d3.extent( raw_data, function( d )
							{ return d[ yVar ]; } ) );

	//criando os eixos com escala default e ticks -- objeto
	var xAxis = d3.axisBottom().scale( xScale )
					.tickFormat(function( d, i ){ 
						return raw_data[ i ][ xVar ] } );
	debugger;

	var yAxis = d3.axisLeft().scale( yScale );

	//adicionando os eixos ao gráfico
	svg.append("g")
			.attr("transform","translate(" + margin.left + "," + height + ")")
			.call( xAxis )
			.selectAll( 'text' )
			.style( 'text-anchor', 'end' )
			.attr( 'dx', '-.10em' )
			.attr( 'dx', '.15em' )
			.attr( 'transform', 'rotate( -65 )' );

	svg.append("g")
			.attr("transform","translate(" + margin.left + "," + margin.bottom + ")")
			.call(yAxis);

};