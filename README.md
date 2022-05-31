# Prices tracker
Prices tracker is an application which get information about products from supported sites. <br>
### Description of the web application:
Main page: ![main_page](https://user-images.githubusercontent.com/33072543/162711847-d8ecfa3b-2cfc-410f-a1fb-887da6ae33a4.png)

<summary><b>Create database and category (step 1):</b></summary>

![create_db_and_cat](https://user-images.githubusercontent.com/33072543/162733295-ed24f17c-b74c-47fb-a1cf-0df684cf81fc.gif)


<summary><b>Select category (step 2):</b></summary>

![select_category](https://user-images.githubusercontent.com/33072543/162735087-38beaca8-2f2a-4071-bebc-b4acb5bb84b5.gif)

<summary><b>Add link in selected category and synchronize info with added links (step 3):</b></summary>

![add_link](https://user-images.githubusercontent.com/33072543/162740466-b02465f2-e1b4-49e0-b954-448d556ba215.gif)

<summary><b>After synchronize info on step 3, the info might be displayed on plot:</b></summary>

![build_clear_plotter](https://user-images.githubusercontent.com/33072543/162741597-2ec8b2fe-28cf-487b-a86b-81dea72677dc.gif)
  
<summary><b>The information about products might be shown as table. In work with table is possible to remove information about the product or disable the need to monitor it:</b></summary>
  
![show_sheet](https://user-images.githubusercontent.com/33072543/162741968-91af9118-5468-4003-ba3f-f5a130c0219a.gif)

### Dependencies:
<ol>
  <li>Python 3.6+</li>
  <li>Web server nginx (optional)</li>
  <li>Docker (optional)</li>
</ol>

### Installation:
```bash
$ pip install -r requirements.txt
```

### Start web application (3 ways):
<summary>First way (use embedded in flask web server):</summary>

Run:
```bash
$ python3 main.py -W
```

<summary>Second way (use nginx and uwsgi):</summary>

Prepare:
```bash
$ sudo apt install nginx
$ sudo cp configs/nginx/nginx.conf /etc/nginx/
$ sudo mkdir -p /etc/nginx/sites-available && sudo mkdir -p /etc/nginx/sites-enabled
$ sudo cp -r configs/nginx/sites-available /etc/nginx/sites-available
$ sudo ln -s /etc/nginx/sites-enabled/web_app.conf /etc/nginx/sites-available/web_app.conf
$ sudo rm -f /etc/nginx/sites-enabled/default && sudo rm -f /etc/nginx/sites-available/default
```

Run:
```bash
$ sudo systemctl start nginx
$ cd web_app
$ uwsgi --ini uwsgi.ini &
```

<summary>Third way (use Docker):</summary>

Prepare:
```bash
$ mkdir databases
$ docker build -t web_application_image .
$ docker volume create web_app_databases
```

Run:
```bash
$ docker run -d -e TZ=$(timedatectl | grep "Time zone" | xargs | cut -d" " -f 3) --rm --name prices_tracker_app -p 80:80 -v web_app_databases:/<path_to_program_directory>/prices_tracker/databases web_application_image
```

Stop:
```bash
$ docker stop prices_tracker_app
```

Delete docker volume:
```bash
$ docker volume rm web_app_databasses
```
