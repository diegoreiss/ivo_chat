const formLogin = $('#formLogin'),
  loginRedirect = formLogin.attr('data-login-redirect');

formLogin.on('submit', function (event) {
  event.preventDefault();

  const data = JSON.stringify({
    'username': $('#inputUsername').val(),
    'password': $('#inputPassword').val(),
  }),
    url = $(this).attr('action'),
    xcsrf = $(this).find('input[name="csrfmiddlewaretoken"]').val();


  $.ajax({
    url: url,
    type: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-CSRFToken': xcsrf,
    },
    data: data,
    success: async function (response) {
      localStorage.setItem('refresh', response.refresh);
      localStorage.setItem('access', response.access);
      console.log(response);

      const data = await getRoleFromCurrentUser(),
        role = data.role;
      
      console.log('role :>> ', role);

      if (!role) {
        window.location.reload();

        return;
      }

      redirectByRole(role);
    },
    error: function (xhr, status, error) {
      console.log('error :>> ', error);
    },
  });

});


function getRoleFromCurrentUser() {
  return $.ajax({
    url: '/api/user/current/',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access')}`,
    },
  });
}

function redirectByRole(role) {
  const redirects = {
    1: '/chat/admin/',
    2: '/chat/',
  }[role]

  window.location.href = redirects
}
