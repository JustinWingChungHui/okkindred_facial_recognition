from secrets import MEDIA_ROOT, MEDIA_URL
import requests

# https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_file(large_thumbnail):

    url = '{0}{1}'.format(MEDIA_URL, large_thumbnail)

    local_filename = MEDIA_ROOT + url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()

        r.close()
    return local_filename