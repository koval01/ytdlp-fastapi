import { VidstackPlayer, VidstackPlayerLayout } from 'https://cdn.vidstack.io/player@1.12.1';

document.addEventListener('DOMContentLoaded', () => {
    const videoPlayerContainer = document.getElementById('videoPlayerContainer');
    const videoId = videoPlayerContainer.getAttribute('data-video-id');
    const secretKey = videoPlayerContainer.getAttribute('data-secret-key');

    async function fetchMedia() {
        const response = await fetch(`/v1/video/${videoId}`, {
            method: 'GET',
            headers: {
                'X-Secret': secretKey
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }

        const data = await response.json();
        const streamUrl = data.manifest_url + ".m3u8";

        if (streamUrl) {
            return { title: data.title, uploader: data.uploader, streamUrl: streamUrl, thumbnailUrl: data.thumbnail, storyboard: null };
        } else {
            throw new Error('Video or audio data not found in the response');
        }
    }

    function setupPlayer(title, streamUrl, thumbnailUrl, storyboard) {
        const player = VidstackPlayer.create({
            target: '#videoPlayerContainer',
            title: title,
            src: streamUrl,
            autoplay: true,
            poster: thumbnailUrl,
            layout: new VidstackPlayerLayout({
                // thumbnails: storyboard,
                smallWhen: 'never'
            }),
        });

        // Update video title in video-info section
        const videoTitleElement = document.querySelector('.video-info h2');
        videoTitleElement.textContent = title;
    }

    fetchMedia()
        .then(({ title, uploader, streamUrl, thumbnailUrl, storyboard }) => {
            setupPlayer(title, streamUrl, thumbnailUrl, storyboard);

            document.title = `${title} - ${uploader}`;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
});
