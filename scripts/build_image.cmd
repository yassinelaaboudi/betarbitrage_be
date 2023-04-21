
REM Build the image
docker build -t selenium_image .

REM Run the image 
docker run -v "C:/Users/Home/Desktop/bet arbitrages/data_docker:/app/data" selenium_image:latest
