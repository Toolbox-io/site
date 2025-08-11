(async () => {
    interface Photo {
        uuid: string;
        url: string; // data URL or blob URL
    }
    
    const gallery = document.getElementById('photo-gallery')!;
    const modal = document.getElementById('photo-modal')!;
    const modalPhoto = document.getElementById('modal-photo') as HTMLImageElement;
    const downloadBtn = document.getElementById('download-photo')!;
    const deleteBtn = document.getElementById('delete-photo')!;
    const galleryPlaceholder = document.getElementById('gallery-placeholder')!;
    
    let photos: Photo[] = [];
    let currentPhoto: Photo | null = null;
    
    function renderGallery() {
        gallery.innerHTML = '';
        if (photos.length === 0) {
            gallery.appendChild(galleryPlaceholder);
        } else {
            photos.forEach(photo => {
                const img = document.createElement('img');
                img.src = photo.url;
                img.className = 'gallery-thumb';
                img.onclick = () => openModal(photo);
                gallery.appendChild(img);
            });
        }
    }
    
    function openModal(photo: Photo) {
        currentPhoto = photo;
        modalPhoto.src = photo.url;
        modal.classList.remove('hidden');
    }
    
    function closeModal() {
        modal.classList.add('hidden');
        currentPhoto = null;
    }
    
    // Modal overlay click closes modal
    modal.querySelector('.modal-overlay')!.addEventListener('click', closeModal);
    
    // Download and delete button events (placeholders)
    downloadBtn.addEventListener('click', () => {
        if (currentPhoto) {
            // TODO: implement download logic
            alert('Download: ' + currentPhoto.uuid);
        }
    });
    deleteBtn.addEventListener('click', () => {
        if (currentPhoto) {
            // TODO: implement delete logic
            alert('Delete: ' + currentPhoto.uuid);
        }
    });
    
    // --- Encryption Utilities ---
    async function deriveKeyFromPasswordHash(passwordHash: string): Promise<CryptoKey> {
        // Use SHA-256 of the password hash as the key material
        const enc = new TextEncoder();
        const hashBuffer = await crypto.subtle.digest('SHA-256', enc.encode(passwordHash));
        return crypto.subtle.importKey(
            'raw',
            hashBuffer,
            { name: 'AES-GCM' },
            false,
            ['encrypt', 'decrypt']
        );
    }

    async function encryptData(data: ArrayBuffer, key: CryptoKey): Promise<{cipher: ArrayBuffer, iv: Uint8Array}> {
        const iv = crypto.getRandomValues(new Uint8Array(12)); // 96-bit IV for AES-GCM
        const cipher = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv },
            key,
            data
        );
        return { cipher, iv };
    }

    async function decryptData(cipher: ArrayBuffer, key: CryptoKey, iv: Uint8Array): Promise<ArrayBuffer> {
        return crypto.subtle.decrypt(
            { name: 'AES-GCM', iv },
            key,
            cipher
        );
    }

    function generateUUID() {
        // RFC4122 v4 compliant UUID
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = crypto.getRandomValues(new Uint8Array(1))[0] % 16;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function getPasswordHash(): string | null {
        return localStorage.getItem('passwordHash');
    }

    // --- Upload Logic ---
    async function handleFileUpload(file: File) {
        const passwordHash = getPasswordHash();
        if (!passwordHash) {
            alert('No password hash found. Please log in again.');
            return;
        }
        const key = await deriveKeyFromPasswordHash(passwordHash);
        const arrayBuffer = await file.arrayBuffer();
        const { cipher, iv } = await encryptData(arrayBuffer, key);
        const uuid = generateUUID();

        // Prepare form data
        const formData = new FormData();
        formData.append('photo_uuid', uuid);
        // Combine IV and cipher for upload
        const ivAndCipher = new Uint8Array(iv.length + cipher.byteLength);
        ivAndCipher.set(iv, 0);
        ivAndCipher.set(new Uint8Array(cipher), iv.length);
        formData.append('file', new Blob([ivAndCipher]), file.name + '.enc');

        // Upload to backend
        const resp = await fetch('/api/photos/upload', {
            method: 'POST',
            body: formData,
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("authToken")}`
            }
        });
        if (!resp.ok) {
            alert('Upload failed: ' + (await resp.text()));
            return;
        }
        // Add to gallery
        const url = URL.createObjectURL(file); // Show original for now (will reload from backend)
        photos.push({ uuid, url });
        renderGallery();
    }

    // --- Download & Decrypt Logic ---
    async function downloadAndDecryptPhoto(uuid: string, filename: string): Promise<string> {
        const passwordHash = getPasswordHash();
        if (!passwordHash) throw new Error('No password hash found.');
        const key = await deriveKeyFromPasswordHash(passwordHash);
        const resp = await fetch(
            `/api/photos/download/${uuid}`, 
            {
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("authToken")}`
                }
            }
        );
        if (!resp.ok) throw new Error('Download failed');
        const blob = await resp.blob();
        const buffer = await blob.arrayBuffer();
        // Extract IV and cipher
        const iv = new Uint8Array(buffer.slice(0, 12));
        const cipher = buffer.slice(12);
        const plain = await decryptData(cipher, key, iv);
        // Convert to data URL for display
        const fileType = filename.split('.').pop()?.toLowerCase() === 'jpg' ? 'image/jpeg' : 'image/png';
        return URL.createObjectURL(new Blob([plain], { type: fileType }));
    }

    // Drag-and-drop upload integration
    function handleDrop(e: DragEvent) {
        e.preventDefault();
        if (e.dataTransfer && e.dataTransfer.files.length > 0) {
            for (const file of Array.from(e.dataTransfer.files)) {
                handleFileUpload(file);
            }
        }
        gallery.classList.remove('dragover');
    }
    
    gallery.addEventListener('dragover', e => {
        e.preventDefault();
        gallery.classList.add('dragover');
    });
    gallery.addEventListener('dragleave', e => {
        e.preventDefault();
        gallery.classList.remove('dragover');
    });
    gallery.addEventListener('drop', handleDrop);
    
    // --- Load and decrypt photos from backend ---
    const checkAuth = await fetch("/api/auth/check-auth", {
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("authToken")}`
        }
    })
    if (!checkAuth.ok) {
        location.href = "/account/login";
        return;
    }

    const resp = await fetch(
        '/api/photos/sync', 
        { 
            "headers": {
                "Authorization": `Bearer ${localStorage.getItem("authToken")}`
            }
        }
    );
    if (!resp.ok) {
        alert('Не удалось загрузить список фото');
        return;
    }
    const data = await resp.json();
    const photoList = data.photos as { uuid: string, filename: string }[];
    photos = [];
    for (const { uuid, filename } of photoList) {
        try {
            const url = await downloadAndDecryptPhoto(uuid, filename);
            photos.push({ uuid, url });
        } catch (e) {
            console.error('Failed to load photo', uuid, e);
        }
    }
    renderGallery();
})();