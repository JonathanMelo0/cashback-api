// SUBSTITUA PELO SEU LINK REAL DO RENDER
const API_URL = "https://cashback-api-1.onrender.com"; 

const btn = document.getElementById("btnCalcular");
const listaHistorico = document.getElementById("listaHistorico");
const resultado = document.getElementById("resultado");

async function atualizarHistorico() {
    // Feedback visual de carregamento
    listaHistorico.innerHTML = "<li>Carregando histórico...</li>";

    try {
        const response = await fetch(`${API_URL}/historico`);
        if (!response.ok) throw new Error();
        
        const dados = await response.json();
        listaHistorico.innerHTML = ""; 

        if (dados.length === 0) {
            listaHistorico.innerHTML = "<li>Nenhum histórico para este IP.</li>";
            return;
        }

        dados.forEach(item => {
            const li = document.createElement("li");
            li.innerHTML = `<strong>${item.tipo.toUpperCase()}</strong>: Compra R$ ${item.valor} ⮕ <span>Cashback R$ ${item.cashback}</span>`;
            listaHistorico.appendChild(li);
        });
    } catch (error) {
        listaHistorico.innerHTML = "<li>O servidor está acordando. Tente atualizar em instantes.</li>";
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

        resultado.innerHTML = `<h3>Seu Cashback: R$ ${data.cashback}</h3>`;
        
        // Atualiza a lista após o novo cálculo
        atualizarHistorico();
    } catch (error) {
        resultado.innerText = "Erro ao conectar. O servidor pode estar em standby.";
    }
});

// Busca o histórico assim que a página abre
document.addEventListener("DOMContentLoaded", atualizarHistorico);