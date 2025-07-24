(() => {
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
    
    // Drag-and-drop upload
    function handleDrop(e: DragEvent) {
        e.preventDefault();
        if (e.dataTransfer && e.dataTransfer.files.length > 0) {
            for (const file of Array.from(e.dataTransfer.files)) {
                // TODO: encrypt and upload file
                alert('Upload: ' + file.name);
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
    
    document.addEventListener('DOMContentLoaded', renderGallery);
})();