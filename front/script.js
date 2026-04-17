const btn = document.getElementById("btnCalcular");
const listaHistorico = document.getElementById("listaHistorico");
const resultado = document.getElementById("resultado");

// COLOQUE O SEU LINK DO RENDER AQUI (TERMINA COM .onrender.com)
const API_URL = "https://cashback-api-1.onrender.com"; 

async function atualizarHistorico() {
    try {
        const response = await fetch(`${API_URL}/historico`);
        const dados = await response.json();
        
        listaHistorico.innerHTML = ""; 

        dados.forEach(item => {
            const li = document.createElement("li");
            // Agora os nomes batem com o que o Python envia
            li.innerHTML = `<strong>${item.tipo.toUpperCase()}</strong>: Compra de R$ ${item.valor} ⮕ Cashback: <span>R$ ${item.cashback}</span>`;
            listaHistorico.appendChild(li);
        });
    } catch (e) {
        console.error("Erro ao carregar histórico:", e);
    }
}

btn.addEventListener("click", async () => {
    const valor = document.getElementById("valorCompra").value;
    const tipo = document.getElementById("tipoCliente").value;
    const cupom = document.getElementById("cupom").value || 0;

    if (!valor) return alert("Digite o valor da compra!");

    resultado.innerText = "Calculando...";

    try {
        const response = await fetch(`${API_URL}/calcular?valor=${valor}&tipo=${tipo}&cupom=${cupom}`);
        const data = await response.json();

        resultado.innerHTML = `<h3>Resultado: R$ ${data.cashback}</h3>`;
        
        // Atualiza a lista após salvar
        atualizarHistorico();
    } catch (error) {
        resultado.innerText = "Erro ao conectar com o servidor.";
    }
});

// Inicia a lista quando o site abre
window.onload = atualizarHistorico;