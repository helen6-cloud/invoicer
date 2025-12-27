document.addEventListener('DOMContentLoaded', function() {
    const cesitField = document.querySelector('#id_cesit');

    function toggle() {

        const sezonGrup = document.getElementById('sezonlar-group');

        const filmGrup = document.querySelector('.field-film-group');

        if (cesitField.value === 'film') {
            if (sezonGrup) sezonGrup.style.display = 'none';
            if (filmGrup) filmGrup.style.display = 'block';
        } else {
            if (sezonGrup) sezonGrup.style.display = 'block';
            if (filmGrup) filmGrup.style.display = 'none';
        }
    }

    if (cesitField) {
        cesitField.addEventListener('change', toggle);
        toggle();
    }
});