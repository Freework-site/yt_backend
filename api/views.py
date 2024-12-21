from django.http import JsonResponse, HttpResponse
import yt_dlp
import os

def get_video_info(request):
    url = request.GET.get('url')  # Get URL from the request

    if not url:
        return JsonResponse({'error': 'URL parameter is required'}, status=400)

    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            best_audio = None

            # Extract m4a audio with the best quality
            for f in info['formats']:
                if f.get('ext') == 'm4a' and f.get('url'):
                    if not best_audio or (f.get('abr', 0) > best_audio.get('abr', 0)):
                        best_audio = f

            # Extract video formats (webm, resolution from 144p to 1080p)
            for f in info['formats']:
                if f.get('url') and f.get('ext') == 'webm' and f.get('vcodec') != 'none':
                    resolution = f"{f.get('width')}x{f.get('height')}"
                    if f.get('height') in [144, 240, 360, 480, 720, 1080]:
                        formats.append({
                            'resolution': resolution,
                            'format_id': f['format_id'],
                            'ext': f['ext'],
                            'url': f['url'],
                            'type': 'video'
                        })

            # Add best audio to formats list
            if best_audio:
                formats.insert(0, {
                    'resolution': 'Audio Only (m4a)',
                    'format_id': best_audio['format_id'],
                    'ext': best_audio['ext'],
                    'url': best_audio['url'],
                    'type': 'audio'
                })

            # Return video information
            return JsonResponse({
                'title': info.get('title'),
                'formats': formats,
                'thumbnail': info.get('thumbnail', ''),
                'description': info.get('description', ''),
                'uploader': info.get('uploader', '')
            })

    except Exception as e:
        return JsonResponse({'error': f'Failed to fetch video info: {str(e)}'}, status=500)


def download_video(request):
    file_url = request.GET.get('file_url')  # Expect the file URL as a GET parameter

    if not file_url:
        return JsonResponse({'error': 'File URL parameter is required'}, status=400)

    try:
        # Use yt-dlp to download the video file
        ydl_opts = {
            'quiet': True,
            'outtmpl': '%(title)s.%(ext)s',  # Save the file with its title and extension
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(file_url, download=True)
            filepath = ydl.prepare_filename(info)

        # Send the file as an HTTP response
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            response['Content-Length'] = os.path.getsize(filepath)
            return response

    except Exception as e:
        return JsonResponse({'error': f'Failed to download video: {str(e)}'}, status=500)

    finally:
        # Clean up downloaded file
        if os.path.exists(filepath):
            os.remove(filepath)
