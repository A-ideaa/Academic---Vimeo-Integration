import os
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Video
import vimeo
import requests
import json
import time

def get_vimeo_client():
    return vimeo.VimeoClient(
        token=settings.VIMEO_ACCESS_TOKEN,
        key=settings.VIMEO_CLIENT_ID,
        secret=settings.VIMEO_CLIENT_SECRET,
        scope=['public', 'private', 'upload']
    )

def test_credentials(request):
    try:
        client = get_vimeo_client()
        response = client.get('/me')
        user_data = response.json()
        
        # Get available scopes
        token_info = client.get('/oauth/verify')
        scopes = token_info.json().get('scope', [])
        
        # Required scopes for our application
        required_scopes = ['public', 'private', 'upload']
        missing_scopes = [scope for scope in required_scopes if scope not in scopes]
        
        # Test upload capability
        upload_test = None
        if 'upload' in scopes:
            try:
                # Try to create a test video container with correct parameters
                test_video_data = {
                    'upload': {
                        'approach': 'tus',
                        'size': '1000'  # Small test size
                    },
                    'name': 'Test Video',
                    'privacy': {
                        'view': 'anybody'
                    }
                }
                
                test_video = client.post('/me/videos', data=test_video_data)
                if test_video.ok:
                    upload_test = "Success - Can create video containers"
                    # Clean up the test video
                    video_uri = test_video.json()['uri']
                    client.delete(video_uri)
                else:
                    upload_test = f"Failed - {test_video.text}"
            except Exception as e:
                upload_test = f"Error - {str(e)}"
        
        return HttpResponse(f"""
            <div style='padding: 20px; font-family: Arial, sans-serif;'>
                <h2>Vimeo Credentials Test</h2>
                <div style='background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;'>
                    <h3>Connection Status: <span style='color: green;'>Success!</span></h3>
                    <p><strong>Authenticated User:</strong> {user_data['name']}</p>
                    <p><strong>User URI:</strong> {user_data['uri']}</p>
                    <p><strong>Available Scopes:</strong> {', '.join(scopes)}</p>
                    <p><strong>Required Scopes:</strong> {', '.join(required_scopes)}</p>
                    {f"<p style='color: red;'><strong>Missing Scopes:</strong> {', '.join(missing_scopes)}</p>" if missing_scopes else ""}
                    {f"<p><strong>Upload Test:</strong> {upload_test}</p>" if upload_test else ""}
                </div>
                <div style='margin-top: 20px;'>
                    <h4>How to Fix Missing Scopes:</h4>
                    <ol>
                        <li>Go to <a href='https://developer.vimeo.com/apps' target='_blank'>Vimeo Developer Apps</a></li>
                        <li>Click on your app</li>
                        <li>Go to "Authentication"</li>
                        <li>Click "Generate Access Token"</li>
                        <li>Select ALL of these scopes:
                            <ul>
                                <li><strong>public</strong> - to view public videos</li>
                                <li><strong>private</strong> - to access private videos</li>
                                <li><strong>upload</strong> - to upload videos</li>
                            </ul>
                        </li>
                        <li>Generate a new token and update your .env file</li>
                    </ol>
                </div>
                <a href='/' class='btn btn-primary'>Back to Home</a>
            </div>
        """)
    except Exception as e:
        return HttpResponse(f"""
            <div style='padding: 20px; font-family: Arial, sans-serif;'>
                <h2>Vimeo Credentials Test</h2>
                <div style='background: #fff3f3; padding: 15px; border-radius: 5px; margin: 10px 0;'>
                    <h3>Connection Status: <span style='color: red;'>Failed!</span></h3>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <p>Please check your .env file and make sure your credentials are correct.</p>
                </div>
                <div style='margin-top: 20px;'>
                    <h4>How to Fix:</h4>
                    <ol>
                        <li>Go to <a href='https://developer.vimeo.com/apps' target='_blank'>Vimeo Developer Apps</a></li>
                        <li>Click on your app</li>
                        <li>Go to "Authentication"</li>
                        <li>Click "Generate Access Token"</li>
                        <li>Select ALL of these scopes:
                            <ul>
                                <li><strong>public</strong> - to view public videos</li>
                                <li><strong>private</strong> - to access private videos</li>
                                <li><strong>upload</strong> - to upload videos</li>
                            </ul>
                        </li>
                        <li>Generate a new token and update your .env file</li>
                    </ol>
                </div>
                <a href='/' class='btn btn-primary'>Back to Home</a>
            </div>
        """)

def home(request):
    videos = Video.objects.all()
    return render(request, 'vimeo_app/home.html', {'videos': videos})

def add_cors_headers(response):
    """Add CORS headers to allow requests from ngrok."""
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response

@csrf_exempt
def upload_video(request):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        return add_cors_headers(response)

    if request.method == 'POST':
        if not request.FILES.get('video'):
            response = HttpResponse(json.dumps({
                'status': 'error',
                'error': 'No video file provided'
            }), content_type='application/json', status=400)
            return add_cors_headers(response)
            
        video_file = request.FILES['video']
        
        # Check file size (500MB limit)
        if video_file.size > 500 * 1024 * 1024:
            response = HttpResponse(json.dumps({
                'status': 'error',
                'error': 'File size exceeds 500MB limit'
            }), content_type='application/json', status=400)
            return add_cors_headers(response)
            
        title = request.POST.get('title', 'Untitled')
        description = request.POST.get('description', '')

        # Create media directory if it doesn't exist
        media_dir = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(media_dir, exist_ok=True)

        # Save video file temporarily with unique name
        file_name = f"{int(time.time())}_{video_file.name}"
        temp_path = os.path.join(media_dir, file_name)
        
        try:
            # Save file in chunks to handle large files
            with open(temp_path, 'wb+') as destination:
                for chunk in video_file.chunks(chunk_size=1024 * 1024):  # 1MB chunks for saving
                    destination.write(chunk)

            try:
                client = get_vimeo_client()
                
                # Verify token and scopes
                token_info = client.get('/oauth/verify')
                scopes = token_info.json().get('scope', [])
                
                if 'upload' not in scopes:
                    raise Exception("Missing 'upload' scope. Please generate a new access token with upload permissions.")
                
                # Create video container with proper size
                video_data = {
                    'upload': {
                        'approach': 'tus',
                        'size': str(video_file.size)
                    },
                    'name': title,
                    'description': description,
                    'privacy': {
                        'view': 'anybody'
                    }
                }
                
                video_uri = client.post('/me/videos', data=video_data)
                if not video_uri.ok:
                    raise Exception(f"Failed to create video container: {video_uri.text}")
                
                upload_data = video_uri.json()
                if 'upload' not in upload_data:
                    raise Exception("No upload URL found in response")
                
                upload_url = upload_data['upload']['upload_link']
                video_uri = upload_data['uri']
                vimeo_id = video_uri.split('/')[-1]
                
                # Upload the video file using TUS protocol
                with open(temp_path, 'rb') as video_file:
                    headers = {
                        'Content-Type': 'application/offset+octet-stream',
                        'Upload-Offset': '0',
                        'Tus-Resumable': '1.0.0',
                        'Content-Length': str(os.path.getsize(temp_path))
                    }
                    
                    upload_response = requests.patch(
                        upload_url,
                        data=video_file,
                        headers=headers,
                        timeout=3600  # 1 hour timeout
                    )
                    
                    if not upload_response.ok:
                        client.delete(video_uri)
                        raise Exception(f"Upload failed: {upload_response.text}")
                
                # Verify upload
                verify_response = client.get(f'/videos/{vimeo_id}')
                if not verify_response.ok:
                    client.delete(video_uri)
                    raise Exception(f"Failed to verify upload: {verify_response.text}")
                
                video_data = verify_response.json()
                
                # Create Video object
                video = Video.objects.create(
                    title=title,
                    description=description,
                    vimeo_id=vimeo_id,
                    thumbnail_url=video_data.get('pictures', {}).get('base_link', ''),
                    video_url=video_data.get('link', '')
                )

                response = HttpResponse(json.dumps({
                    'status': 'complete',
                    'success': True,
                    'vimeo_id': vimeo_id
                }), content_type='application/json')
                return add_cors_headers(response)
                
            except Exception as e:
                error_message = str(e)
                print(f"Error details: {error_message}")
                response = HttpResponse(json.dumps({
                    'status': 'error',
                    'error': error_message
                }), content_type='application/json', status=500)
                return add_cors_headers(response)
            
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            error_message = f"Error handling file: {str(e)}"
            response = HttpResponse(json.dumps({
                'status': 'error',
                'error': error_message
            }), content_type='application/json', status=500)
            return add_cors_headers(response)

    return render(request, 'vimeo_app/upload.html')

@csrf_exempt
def delete_video(request, video_id):
    if request.method == 'OPTIONS':
        response = HttpResponse()
        return add_cors_headers(response)

    if request.method == 'POST':
        try:
            video = get_object_or_404(Video, id=video_id)
            
            # Delete from Vimeo
            client = get_vimeo_client()
            response = client.delete(f'/videos/{video.vimeo_id}')
            
            if not response.ok:
                raise Exception(f"Failed to delete video from Vimeo: {response.text}")
            
            # Delete from database
            video.delete()
            
            messages.success(request, 'Video deleted successfully!')
            response = redirect('home')
            return add_cors_headers(response)
        except Exception as e:
            messages.error(request, f'Error deleting video: {str(e)}')
            response = redirect('home')
            return add_cors_headers(response)
    
    response = redirect('home')
    return add_cors_headers(response)

def video_player(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    videos = Video.objects.all().order_by('upload_date')
    return render(request, 'vimeo_app/video_player.html', {
        'video': video,
        'videos': videos
    })

def check_progress(request, vimeo_id):
    """Check the upload progress of a video on Vimeo."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponse('Invalid request', status=400)
        
    try:
        client = get_vimeo_client()
        response = client.get(f'/videos/{vimeo_id}')
        
        if not response.ok:
            return HttpResponse(json.dumps({
                'status': 'error',
                'error': 'Failed to get video status'
            }), content_type='application/json', status=500)
            
        video_data = response.json()
        upload_status = video_data.get('upload', {}).get('status')
        
        if upload_status == 'complete':
            return HttpResponse(json.dumps({
                'status': 'complete',
                'success': True
            }), content_type='application/json')
        elif upload_status == 'in_progress':
            # Get upload progress
            progress = video_data.get('upload', {}).get('progress', 0)
            return HttpResponse(json.dumps({
                'status': 'uploading',
                'progress': progress
            }), content_type='application/json')
        else:
            return HttpResponse(json.dumps({
                'status': 'error',
                'error': f'Unknown upload status: {upload_status}'
            }), content_type='application/json', status=500)
            
    except Exception as e:
        return HttpResponse(json.dumps({
            'status': 'error',
            'error': str(e)
        }), content_type='application/json', status=500)

@csrf_exempt
def check_video_status(request, vimeo_id):
    """Check the processing status of a video and update its thumbnail."""
    if request.method == 'OPTIONS':
        response = HttpResponse()
        return add_cors_headers(response)

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        response = HttpResponse('Invalid request', status=400)
        return add_cors_headers(response)
        
    try:
        client = get_vimeo_client()
        response = client.get(f'/videos/{vimeo_id}')
        
        if not response.ok:
            response = HttpResponse(json.dumps({
                'status': 'error',
                'error': 'Failed to get video status'
            }), content_type='application/json', status=500)
            return add_cors_headers(response)
            
        video_data = response.json()
        
        # Get the video object
        try:
            video = Video.objects.get(vimeo_id=vimeo_id)
        except Video.DoesNotExist:
            response = HttpResponse(json.dumps({
                'status': 'error',
                'error': 'Video not found in database'
            }), content_type='application/json', status=404)
            return add_cors_headers(response)
        
        # Check transcode status
        transcode_status = video_data.get('transcode', {}).get('status')
        
        # Check if the video is ready
        if transcode_status == 'complete':
            # Update thumbnail and status
            pictures = video_data.get('pictures', {})
            if pictures:
                # Get the largest available thumbnail
                sizes = pictures.get('sizes', [])
                if sizes:
                    largest_thumb = max(sizes, key=lambda x: x.get('width', 0))
                    video.thumbnail_url = largest_thumb.get('link', '')
            video.status = 'available'
            video.save()
            
            response = HttpResponse(json.dumps({
                'status': 'available',
                'thumbnail_url': video.thumbnail_url
            }), content_type='application/json')
            return add_cors_headers(response)
        else:
            # Video is still processing
            response = HttpResponse(json.dumps({
                'status': 'processing'
            }), content_type='application/json')
            return add_cors_headers(response)
            
    except Exception as e:
        print(f"Error checking video status: {str(e)}")
        response = HttpResponse(json.dumps({
            'status': 'error',
            'error': str(e)
        }), content_type='application/json', status=500)
        return add_cors_headers(response)
