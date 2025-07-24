configure_local_environment:
	docker-compose exec localstack aws --endpoint-url=http://localhost:4566 configure set default.region us-east-1
	docker-compose exec localstack aws --endpoint-url=http://localhost:4566 configure set aws_access_key_id 'temp'
	docker-compose exec localstack aws --endpoint-url=http://localhost:4566 configure set aws_secret_access_key 'temp'
	docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis create-stream --stream-name cloud-sentinel --shard-count 1