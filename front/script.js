const btn = document.getElementById("btnCalcular");
const listaHistorico = document.getElementById("listaHistorico");
const resultado = document.getElementById("resultado");

// 1. AQUI VOCÊ COLA O SEU LINK DO RENDER ENTRE AS ASPAS
const API_URL = "https://cashback-api-1.onrender.com"; 

// FUNÇÃO QUE BUSCA DO BANCO
async function atualizarHistorico() {
    try {
        const response = await fetch(`${API_URL}/historico`);
        const dados = await response.json();
        
        listaHistorico.innerHTML = ""; 

        dados.forEach(item => {
            const li = document.createElement("li");
            // AJUSTADO: Usando os nomes que a sua API realmente envia (tipo, valor, cashback)
            li.innerText = `Cliente: ${item.tipo} | Valor: R$ ${item.valor} | Cashback: R$ ${item.cashback}`;
            listaHistorico.appendChild(li);
        });
    } catch (e) {
        console.error("Erro ao carregar histórico:", e);
    }
}

// BOTÃO CALCULAR
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

        resultado.innerText = `Cashback: R$ ${data.cashback}`;
        
        // Atualiza a lista com os dados do banco
        atualizarHistorico();
    } catch (error) {
        resultado.innerText = "Erro ao conectar com a API.";
        console.error(error);
    }
});

// CARREGA ASSIM QUE ABRE O SITE
window.onload = atualizarHistorico;