$(document).ready(function() {
    const accessToken = localStorage.getItem('access');

    if (!accessToken) window.location.href = '/auth/login/';
});

// document.addEventListener("DOMContentLoaded", function () {
//     console.log('cu  :>> ');
//     const RASA_URL = 'http://localhost:5005/';

//     const socket = io(RASA_URL);

//     socket.on('connect', function () {
//         console.log('socket connected :>> ');
//     });

//     socket.on('connect_error', (error) => {
//         console.log('error :>> ', error);
//     });

//     const inputAluno = document.querySelector(".input-label");
//     const messagesDiv = document.querySelector(".messages");

//     function adicionarMensagem(mensagem, deAluno = true) {
//         const mensagemDiv = document.createElement("div");
//         mensagemDiv.classList.add("mensagem");
//         mensagemDiv.textContent = mensagem;

//         if (deAluno) {
//             mensagemDiv.classList.add("aluno");
//         } else {
//             mensagemDiv.classList.add("resposta");
//         }

//         messagesDiv.appendChild(mensagemDiv);
//         messagesDiv.scrollTop = messagesDiv.scrollHeight;
//     }

//     function enviarMensagem() {
//         const mensagem = inputAluno.value.trim();
//         if (mensagem !== "") {
//             socket.emit('user_uttered', {
//                 'message': mensagem,
//             })
//             adicionarMensagem(mensagem, true);
//             // Simulação de resposta do bot após um pequeno atraso
//             // setTimeout(function() {
//             //     adicionarMensagem("Oi amiguinho", false);
//             // }, 1000);
//             inputAluno.value = ""; // Limpa o campo de entrada
//         }
//     }

//     document.querySelector(".btn-enviar").addEventListener("click", enviarMensagem);

//     inputAluno.addEventListener("keypress", function (event) {
//         if (event.key === "Enter") {
//             enviarMensagem();
//         }
//     });

//     socket.on('bot_uttered', function (response) {
//       console.log("Bot uttered:", response);
//       if (response.text) {
//         adicionarMensagem(response.text, false);
//       }
//     });
// });
