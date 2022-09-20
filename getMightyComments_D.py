buffer = "";

if input("PRESS ANY KEY") != 0:
  import requests
  import json
  import sys
  import os
  from datetime import datetime

  URL = 'https://www.googleapis.com/youtube/v3/'
  # ここにAPI KEYを入力
  API_KEY = ''
  
  try:
      assert API_KEY != '';
  except:  
      input("ERROR: OPEN CODE AND SET YOUTUBE API KEY");
      exit();
  PLAYLIST_IDs = ["UUv3DBWI1aZVYiq-WcARA83g", "UUJo_tEfYUMAYZXqRtrRt0ww"];
  SKIPCOUNT = input("PLEASE INPUT SKIPCOUNT");
  while not SKIPCOUNT.isdigit():
    SKIPCOUNT = input("ERROR: NONINTEGER CHARACTER(S) DETECTED");
    
  SKIPCOUNT = int(SKIPCOUNT);  

  tasks = [];
  f = None;

  def gettasks(id, next_page_token):
     
      params = {
        'key': API_KEY,
        'part': 'snippet',
        'playlistId': id,
        'order': 'relevance',
        'textFormat': 'plaintext',
        'maxRefsults': 100,
      }
      if next_page_token is not None:
        params['pageToken'] = next_page_token
      response = requests.get(URL + 'playlistItems', params=params)
      resource = response.json()
      
      try:
        assert "error" not in resource;
      except:
        print(resource["error"]["code"], resource["error"]["errors"][0]["message"]);
        sys.exit(input("An Error Occured."));
      for e in resource['items']:
        tasks.append([e["snippet"]['resourceId']['videoId'], e["snippet"]['publishedAt'][:10]]);
      
          
      if "nextPageToken" in resource:
        gettasks(id, resource["nextPageToken"]);


  def print_video_comment(no, video_id, next_page_token):
    global buffer
    
    params = {
      'key': API_KEY,
      'part': 'snippet',
      'videoId': video_id,
      'order': 'relevance',
      'textFormat': 'plaintext',
      'maxResults': 100,
    }
    if next_page_token is not None:
      params['pageToken'] = next_page_token
    response = requests.get(URL + 'commentThreads', params=params)
    resource = response.json()


    try:
        assert "error" not in resource;
    except:
        print(resource["error"]["code"], resource["error"]["errors"][0]["message"]);
        f.write(buffer);
        f.close();
        exit(input("An Error Occured."));
        
    for comment_info in resource['items']:
      # コメント
      text = comment_info['snippet']['topLevelComment']['snippet']['textDisplay']
      # 返信数
      reply_cnt = comment_info['snippet']['totalReplyCount']
      # ユーザー名
      user_name = comment_info['snippet']['topLevelComment']['snippet']['authorDisplayName']
      # Id
      parentId = comment_info['snippet']['topLevelComment']['id']
      # 日付
      published_at = comment_info['snippet']['topLevelComment']['snippet']['publishedAt']
      buffer+= '{}\t{}\t{}\t{}\t{}'.format(no, text.replace('\r', '\n').replace('\n', ' '), user_name, published_at, parentId) + "\n";
      #print("  " + '{}\t{}\t{}\t{}'.format(no, text.replace('\r', '\n').replace('\n', ' '), user_name, published_at) + "\n");
      if len(buffer) > 5000:
        f.write(buffer);
        buffer = "";
      if reply_cnt > 0:
         cno = 1
         print_video_reply(no, cno, video_id, None, parentId)
      no = no + 1
    if 'nextPageToken' in resource:
      print_video_comment(no, video_id, resource["nextPageToken"])

  def print_video_reply(no, cno, video_id, next_page_token, id):
    global buffer
    params = {
      'key': API_KEY,
      'part': 'snippet',
      'videoId': video_id,
      'textFormat': 'plaintext',
      'maxResults': 50,
      'parentId': id,
    }

    stack = [];

    response = requests.get(URL + 'comments', params=params)
    resource = response.json()

    try:
        assert "error" not in resource;
    except:
        print(resource["error"]["code"], resource["error"]["errors"][0]["message"]);
        f.write(buffer);
        f.close();
        
        sys.exit(input("An Error Occured."));

    for comment_info in resource["items"]:
      j = dict();
      j['text'] = comment_info['snippet']['textDisplay']
      j['user_name'] = comment_info['snippet']['authorDisplayName']
      j['published_at'] = comment_info['snippet']['publishedAt']
      j['id'] = comment_info['id']
      stack.append(j);

    requests.get(URL + 'comments', params=params)

    while 'nextPageToken' in resource:
      params['pageToken'] = resource["nextPageToken"]
      response = requests.get(URL + 'comments', params=params)
      resource = response.json()
      
      try:
          assert "error" not in resource;
      except:
          print(resource["error"]["code"], resource["error"]["errors"][0]["message"]);
          sys.exit(input("An Error Occured."));

      for comment_info in resource['items']:
        j = dict();
        j['text'] = comment_info['snippet']['textDisplay']
        j['user_name'] = comment_info['snippet']['authorDisplayName']
        j['published_at'] = comment_info['snippet']['publishedAt']
        j['id'] = comment_info['id']
        try:
          stack.append(j);
        except:
          print("stack overflow: size " + str(len(stack)));
          exit();

    while len(stack):
      comment_info = stack.pop();
      text = comment_info['text']
      user_name = comment_info['user_name']
      published_at = comment_info['published_at']
      commentid = comment_info['id'];

      buffer+= '{}-{:0=3}\t{}\t{}\t{}\t{}'.format(no, cno, text.replace('\r', '\n').replace('\n', ' '), user_name, published_at, commentid) + "\n"

      if len(buffer) > 5000:
        f.write(buffer);
        buffer = "";
      
      cno = cno + 1

  for id in PLAYLIST_IDs:
    gettasks(id, None);
    
  os.makedirs('./MightyComments', exist_ok=True);
  
  while len(tasks):
    temp = tasks.pop(0);
    if SKIPCOUNT:
      print("skipped " + temp[0] + ": remaining ({})".format(SKIPCOUNT-1))
      SKIPCOUNT-= 1;
      continue;
    video_id = temp[0]
    published_at = temp[1];
    path = "MightyComments/" + published_at + "_" + video_id + ".txt";
    print("now exporting to " + published_at + "_" + video_id + ".txt")
    no = 1
    f = open(path, mode='w', encoding='utf-8');
    print_video_comment(no, video_id, None)
    f.write(buffer);
    buffer = "";
    os.system('cls')
    f.close();
    
  print("Done.");
