all: unarchive_data read_hypersweep_data

unarchive_data:
	@echo "Unarchiving data"; \
	for file in archived_data/*.tar.gz; do\
		tar xf $$file --directory resource_data/; \
	done;\
	echo "Done unarchiving data"

read_hypersweep_data:
	@echo "Reading hypersweep data"; \
	python read_hypersweep_summary.py; \
	rm resource_data/hypersweep.summaries; \
	echo "Done reading hypersweep data"
	
clean:
	@echo "Cleaning..."; \
	rm resource_data/*; \
	echo "Done cleaning."	

