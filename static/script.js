function update_max_files() {
    const checkbox = document.getElementById("add_tray_toggle");
    const label = document.getElementById("max_files_label");
    label.innerText = `Select up to ${originalMaxSize - checkbox.checked} images:`;
}