SELECT su.subject_id, su.subject_name, sp.species_name, su.date_of_birth
FROM subject as su
JOIN species as sp
ON su.species_id = sp.species_id;


SELECT e.experiment_id, su.subject_id, sp.species_name, e.experiment_date, et.type_name, e.score, 2
FROM subject as su
JOIN species as sp
ON su.species_id = sp.species_id
JOIN experiment as e
ON su.subject_id = e.subject_id
JOIN experiment_type as et
ON e.experiment_type_id = et.experiment_type_id
;
