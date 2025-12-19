// ------------------------------------------------------------------
// 1. KONFIGURASI API
// ------------------------------------------------------------------
const API_BASE_URL = "https://i80a8lcfm2.execute-api.us-east-1.amazonaws.com/prod";

// ------------------------------------------------------------------
// 2. FUNGSI API (FETCHER & SENDER)
// ------------------------------------------------------------------

// Mengambil status semua device dari DynamoDB (via Lambda & API Gateway)
async function fetchAllDevices() {
    try {
        const response = await fetch(`${API_BASE_URL}/devices`);
        if (!response.ok) throw new Error("Gagal mengambil data");
        return await response.json();
    } catch (error) {
        console.error("Polling Error:", error);
        return [];
    }
}

// Mengirim perintah ke satu device
async function sendCommand(deviceId, command, value) {
    console.log(`Sending: ${deviceId} -> ${command}: ${value}`);
    try {
        await fetch(`${API_BASE_URL}/command`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deviceId: deviceId,
                command: command,
                value: value
            })
        });
    } catch (error) {
        console.error("Command Error:", error);
    }
}

// ------------------------------------------------------------------
// 3. LOGIKA SMART LAMP (Bisa dipakai ulang di semua kamar)
// ------------------------------------------------------------------
function initSmartLamp(config) {
    const { deviceId, toggleBtn, glowEl, sliderEl, valueEl, colorEl } = config;

    let localState = { status: "OFF", brightness: 50, color: "#ffffff" };

    // --- A. FUNGSI UPDATE TAMPILAN (UI) ---
    function updateLampUI(state) {
        // Update status ON/OFF
        const isOn = state.status === "ON";
        if (isOn) {
            toggleBtn.textContent = "ON";
            toggleBtn.className = "px-4 py-2 rounded-xl font-semibold bg-green-500 text-white transition";
        } else {
            toggleBtn.textContent = "OFF";
            toggleBtn.className = "px-4 py-2 rounded-xl font-semibold bg-gray-300 text-gray-900 hover:bg-gray-400 transition";
        }

        // Update Slider & Text
        if (sliderEl) sliderEl.value = state.brightness;
        if (valueEl) valueEl.textContent = state.brightness + "%";
        if (colorEl) colorEl.value = state.color || "#ffffff";

        // Update Glow Effect
        if (!isOn) {
            glowEl.style.background = "#222";
            glowEl.style.boxShadow = "none";
        } else {
            const intensity = state.brightness / 10;
            const c = state.color || "#ffffff";
            glowEl.style.background = c;
            glowEl.style.boxShadow = `0 0 ${10 * intensity}px ${c}, 0 0 ${25 * intensity}px ${c}`;
        }

        // Simpan state lokal
        localState = { ...state };
    }

    // --- B. EVENT LISTENERS (User Interactions) ---

    // 1. Toggle Button
    toggleBtn.addEventListener("click", () => {
        const newState = localState.status === "ON" ? "OFF" : "ON";
        // Update UI segera (optimistic UI) agar terasa cepat
        updateLampUI({ ...localState, status: newState });
        // Kirim ke AWS
        sendCommand(deviceId, "set_status", newState);
    });

    // 2. Brightness Slider (Gunakan 'change' agar tidak spam API saat digeser)
    sliderEl.addEventListener("change", (e) => {
        const val = parseInt(e.target.value);
        updateLampUI({ ...localState, brightness: val });
        sendCommand(deviceId, "set_brightness", val);
    });

    // Update visual saat digeser (input event) tanpa kirim API
    sliderEl.addEventListener("input", (e) => {
        valueEl.textContent = e.target.value + "%";
        // Update glow realtime tanpa kirim data
        const tempState = { ...localState, brightness: e.target.value };
        updateLampUI(tempState);
    });

    // 3. Color Picker
    if (colorEl) {
        colorEl.addEventListener("change", (e) => {
            const val = e.target.value;
            updateLampUI({ ...localState, color: val });
            sendCommand(deviceId, "set_color", val);
        });
    }

    // --- C. POLLING (Sinkronisasi Otomatis) ---
    // Fungsi ini akan dipanggil oleh Polling Manager global di bawah
    return {
        deviceId: deviceId,
        updateFromCloud: (cloudData) => {
            // Jika data cloud berbeda dengan lokal, update UI
            // (Cloud adalah "Single Source of Truth")
            if (cloudData) {
                // Mapping data DynamoDB ke format UI kita
                // Pastikan nama field sesuai dengan yang disimpan Lambda (decimal convert ke number)
                const newState = {
                    status: cloudData.status || "OFF",
                    brightness: Number(cloudData.brightness) || 0,
                    color: cloudData.color || "#ffffff"
                };
                updateLampUI(newState);
            }
        }
    };
}

// ------------------------------------------------------------------
// 4. LOGIKA SMART LOCK (VERSI ADMIN DASHBOARD)
// ------------------------------------------------------------------
function initSmartLock(config) {
    const {
        deviceId,
        iconWrapperEl,
        iconEl,
        statusTextEl,
        toggleBtnEl
    } = config;

    let localState = { status: "LOCKED" };

    // --- A. UPDATE UI ---
    function updateLockUI(state) {
        const isLocked = state.status === "LOCKED";

        if (isLocked) {
            // TAMPILAN TERKUNCI (MERAH)
            if(iconWrapperEl) iconWrapperEl.className = "p-6 rounded-full bg-red-100 mb-4 transition-colors duration-500";
            if(iconEl) iconEl.textContent = "🔒";

            if(statusTextEl) {
                statusTextEl.textContent = "LOCKED";
                statusTextEl.className = "text-2xl font-bold text-red-600 transition-colors";
            }

            // Tombol berubah menjadi "Buka Kunci"
            if(toggleBtnEl) {
                toggleBtnEl.innerHTML = `<span>🔓 Remote Unlock</span>`;
                toggleBtnEl.className = "w-full py-3 px-6 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 active:scale-95 transition-all shadow-lg flex items-center justify-center gap-2";
            }

        } else {
            // TAMPILAN TERBUKA (HIJAU)
            if(iconWrapperEl) iconWrapperEl.className = "p-6 rounded-full bg-green-100 mb-4 transition-colors duration-500";
            if(iconEl) iconEl.textContent = "🔓";

            if(statusTextEl) {
                statusTextEl.textContent = "UNLOCKED";
                statusTextEl.className = "text-2xl font-bold text-green-600 transition-colors";
            }

            // Tombol berubah menjadi "Kunci Kembali"
            if(toggleBtnEl) {
                toggleBtnEl.innerHTML = `<span>🔒 Remote Lock</span>`;
                toggleBtnEl.className = "w-full py-3 px-6 rounded-xl font-bold text-white bg-red-500 hover:bg-red-600 active:scale-95 transition-all shadow-lg flex items-center justify-center gap-2";
            }
        }
    }

    // --- B. EVENT LISTENER (TOMBOL TOGGLE) ---
    if (toggleBtnEl) {
        toggleBtnEl.addEventListener("click", () => {
            // Cek status sekarang, lalu balikkan
            const currentStatus = localState.status;
            const newStatus = currentStatus === "LOCKED" ? "UNLOCKED" : "LOCKED";

            // 1. Update UI segera (biar responsif)
            updateLockUI({ status: newStatus });
            localState.status = newStatus;

            // 2. Kirim perintah ke AWS
            // Perhatikan: command-nya 'set_status', value-nya 'LOCKED'/'UNLOCKED'
            sendCommand(deviceId, "set_status", newStatus);
        });
    }

    // --- C. SYNC DENGAN CLOUD ---
    return {
        deviceId: deviceId,
        updateFromCloud: (cloudData) => {
            if (cloudData && cloudData.status) {
                localState.status = cloudData.status;
                updateLockUI(localState);
            }
        }
    };
}

// ------------------------------------------------------------------
// 5. LOGIKA SMART THERMOMETER 🌡️
// ------------------------------------------------------------------
function initSmartThermometer(config) {
    const {
        deviceId,
        tempValueEl,    // Elemen angka suhu
        humidValueEl,   // Elemen angka kelembaban
        unitBtnEl,      // Tombol ganti unit
        lastUpdateEl    // (Opsional) Teks "Last updated..."
    } = config;

    let localState = {
        display_unit: 'C',
        display_temperature: 0,
        humidity: 0
    };

    // --- A. UPDATE UI ---
    function updateThermoUI(state) {
        // 1. Update Suhu & Unit
        if (tempValueEl) {
            // Tampilkan 1 angka di belakang koma
            const val = parseFloat(state.display_temperature).toFixed(1);
            const unit = state.display_unit || 'C';
            tempValueEl.textContent = `${val}°${unit}`;
        }

        // 2. Update Kelembaban
        if (humidValueEl) {
            humidValueEl.textContent = `${state.humidity}%`;
        }

        // 3. Update Tombol (Visual Feedback)
        if (unitBtnEl) {
            const nextUnit = state.display_unit === 'C' ? 'F' : 'C';
            unitBtnEl.textContent = `Switch to °${nextUnit}`;
        }

        // 4. Update Timestamp (jika ada)
        if (lastUpdateEl && state.timestamp) {
            const date = new Date(state.timestamp * 1000);
            lastUpdateEl.textContent = "Last update: " + date.toLocaleTimeString();
        }
    }

    // --- B. INTERAKSI TOMBOL ---
    if (unitBtnEl) {
        unitBtnEl.addEventListener("click", () => {
            // Tentukan unit target (kebalikan dari sekarang)
            const targetUnit = localState.display_unit === 'C' ? 'F' : 'C';

            // Kirim perintah ke AWS
            // Python akan menerima ini -> ubah state -> lapor balik -> UI update otomatis
            sendCommand(deviceId, "set_unit", targetUnit);

            // (Opsional) Loading state di tombol
            unitBtnEl.textContent = "Switching...";
        });
    }

    // --- C. SYNC CLOUD ---
    return {
        deviceId: deviceId,
        updateFromCloud: (cloudData) => {
            if (cloudData) {
                // Mapping data dari JSON Python
                localState.display_temperature = cloudData.display_temperature || 0;
                localState.display_unit = cloudData.display_unit || 'C';
                localState.humidity = cloudData.humidity || 0;
                localState.timestamp = cloudData.timestamp;

                updateThermoUI(localState);
            }
        }
    };
}

// ------------------------------------------------------------------
// 7. GLOBAL POLLING MANAGER
// ------------------------------------------------------------------
const registeredDevices = [];

function registerDevice(deviceObj) {
    registeredDevices.push(deviceObj);
}

// Jalankan polling setiap 2 detik
setInterval(async () => {
    const allData = await fetchAllDevices(); // Array dari DynamoDB

    registeredDevices.forEach(localDevice => {
        // Cari data spesifik untuk device ini di dalam array cloud
        const cloudData = allData.find(d => d.deviceId === localDevice.deviceId);
        if (cloudData) {
            localDevice.updateFromCloud(cloudData);
        }
    });
}, 2000);