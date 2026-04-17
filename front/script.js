const btn = document.getElementById("btnCalcular");
const listaHistorico = document.getElementById("listaHistorico");
const API_URL = "http://127.0.0.1:8000";

// FUNÇÃO QUE BUSCA DO BANCO
async function atualizarHistorico() {
    try {
        const response = await fetch(`${API_URL}/historico`);
        const dados = await response.json();
        
        listaHistorico.innerHTML = ""; // Limpa a lista antes de atualizar

        dados.forEach(item => {
            const li = document.createElement("li");
            li.innerText = `Cliente: ${item.tipo_cliente} | Valor: R$ ${item.valor_compra} | Cashback: R$ ${item.valor_cashback}`;
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

    const response = await fetch(`${API_URL}/calcular?valor=${valor}&tipo=${tipo}&cupom=${cupom}`);
    const data = await response.json();

    document.getElementById("resultado").innerText = `Cashback: R$ ${data.cashback}`;
    
    // Chama a função para atualizar a lista com o que acabou de ser salvo no banco
    atualizarHistorico();
});

// CARREGA ASSIM QUE ABRE O SITE
window.onload = atualizarHistorico;