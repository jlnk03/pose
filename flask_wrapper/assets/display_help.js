

document.onload = function() {
  const arm_path_title = document.getElementById('arm_path_title');
  const arm_path_help = document.getElementById('arm_path_help');

    arm_path_title.addEventListener('click', () => {
        arm_path_help.classList.toggle('hidden');
    })
}