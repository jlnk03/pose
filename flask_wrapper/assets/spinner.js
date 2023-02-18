document.addEventListener("DOMContentLoaded", () => {
  const unsubscribe = document.getElementById('unsubscribe');
  const spinner = document.getElementById('spinner');
  const buttonText = document.getElementById('button-text');

  const reactivate = document.getElementById('reactivate');
  const reactivateSpinner = document.getElementById('spinner-reactivate');
  const reactivateText = document.getElementById('reactivate-text');

  if (unsubscribe) {
    unsubscribe.addEventListener('click', () => {
      unsubscribe.setAttribute('disabled', 'disabled');
      spinner.classList.remove('hidden');
      buttonText.innerText = 'Unsubscribing...';
    setTimeout(() => {
              window.location.replace("/unsubscribe")
      }, 100)
    })
  }

  if (reactivate) {
    reactivate.addEventListener('click', () => {
      reactivate.setAttribute('disabled', 'disabled');
      reactivateSpinner.classList.remove('hidden');
      reactivateText.innerText = 'Reactivating...';
      setTimeout(() => {
          window.location.replace("/reactivate")
      }, 100)
    })
  }
});
