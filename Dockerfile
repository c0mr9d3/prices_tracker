FROM python:latest

RUN apt-get update && apt-get install -y nginx python3-pip && apt-get clean

ARG username=web_operator
ARG app_path=/home/$username/prices_tracker
ARG uid=1100
RUN useradd -m -u $uid $username
RUN mkdir -p $app_path

COPY configs/nginx/nginx.conf /etc/nginx
COPY configs/nginx/sites-available/web_app.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/web_app.conf /etc/nginx/sites-enabled/
RUN rm /etc/nginx/sites-enabled/default
RUN rm /etc/nginx/sites-available/default
COPY . $app_path
WORKDIR $app_path

RUN mkdir -p databases
RUN pip3 install -r requirements.txt
RUN chown -R $username:$username $app_path

EXPOSE 80
CMD ["bash", "run_web.sh", "web_operator"]
