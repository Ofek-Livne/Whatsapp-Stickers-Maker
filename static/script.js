function update_max_files() {
    const checkbox = document.getElementById("add_tray_toggle");
    const label = document.getElementById("max_files_label");
    label.innerText = `Select up to ${originalMaxSize - checkbox.checked} images:`;
}

document.getElementById('files').addEventListener('change', function (event) {
        const files = event.target.files;
        const preview = document.getElementById('image-preview');
        preview.innerHTML = '';

        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.width = '150px';
                img.style.margin = '0.5em';
                preview.appendChild(img);
            }
        }
    });
