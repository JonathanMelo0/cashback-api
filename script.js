const btn = document.getElementById("btnCalcular");
const resultado = document.getElementById("resultado");
const listaHistorico = document.getElementById("listaHistorico");

// ATENÇÃO: Substitua pelo link que aparece no seu Dashboard do Render
const API_URL = "https://COLE_AQUI_SEU_LINK_DO_RENDER.onrender.com"; 

// Função para buscar o histórico do banco de dados
async function carregarHistorico() {
    try {
        const response = await fetch(`${API_URL}/historico`);
        const dados = await response.json();
        
        listaHistorico.innerHTML = "";

        dados.forEach(item => {
            const li = document.createElement("li");
            // AJUSTE: Usando os nomes que a sua API Python realmente envia (tipo, valor, cashback)
            li.innerText = `Cliente: ${item.tipo} | Compra: R$ ${item.valor} | Cashback: R$ ${item.cashback}`;
            listaHistorico.appendChild(li);
        });
    } catch (error) {
        console.error("Erro ao carregar histórico:", error);
    }
}

// Evento do botão Calcular
btn.addEventListener("click", async () => {
    const valor = document.getElementById("valorCompra").value;
    const tipo = document.getElementById("tipoCliente").value;
    const cupom = document.getElementById("cupom").value || 0;

    if (!valor || valor <= 0) {
        resultado.innerText = "Digite um valor válido.";
        return;
    }

    resultado.innerText = "Calculando...";

    try {
        const response = await fetch(`${API_URL}/calcular?valor=${valor}&tipo=${tipo}&cupom=${cupom}`);
        const data = await response.json();

        if (data.cashback !== undefined) {
            resultado.innerText = `Cashback: R$ ${data.cashback}`;
            // Atualiza a lista logo após o cálculo
            carregarHistorico();
        } else {
            resultado.innerText = "Erro ao processar cálculo.";
        }

    } catch (error) {
        resultado.innerText = "Erro ao conectar com a API. Verifique se ela está ativa.";
    }
});

// Carrega o histórico assim que a página abre
window.onload = carregarHistorico;