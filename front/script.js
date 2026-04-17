const btn = document.getElementById("btnCalcular");
const resultado = document.getElementById("resultado");
const listaHistorico = document.getElementById("listaHistorico");
const API_URL = "https://cashback-api-1.onrender.com";
// Função para buscar o histórico do banco de dados
async function carregarHistorico() {
    try {
        const response = await fetch(`${API_URL}/historico`);
        const dados = await response.json();
        
        // Limpa a lista antes de preencher
        listaHistorico.innerHTML = "";

        dados.forEach(item => {
            const li = document.createElement("li");
            li.innerText = `Cliente: ${item.tipo_cliente} | Compra: R$ ${item.valor_compra} | Cashback: R$ ${item.valor_cashback}`;
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

    try {
        const response = await fetch(`${API_URL}/calcular?valor=${valor}&tipo=${tipo}&cupom=${cupom}`);
        const data = await response.json();

        resultado.innerText = `Cashback: R$ ${data.cashback}`;

        // Atualiza a lista de histórico buscando os dados novos do banco
        carregarHistorico();

    } catch (error) {
        resultado.innerText = "Erro ao conectar com a API.";
    }
});

// Carrega o histórico assim que a página abre
window.onload = carregarHistorico;