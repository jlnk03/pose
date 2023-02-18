document.addEventListener("DOMContentLoaded", () => {
  const del = document.getElementById('delete');
  const spinner = document.getElementById('spinner');
  const buttonText = document.getElementById('button-text');

  if (del) {
    del.addEventListener('click', () => {
      del.setAttribute('disabled', 'disabled');
      spinner.classList.remove('hidden');
      buttonText.innerText = 'Deleting...';
    setTimeout(() => {
              window.location.replace("/delete_profile_final")
      }, 100)
    })
  }
});
