SELECT su.subject_id, su.subject_name, sp.species_name, su.date_of_birth
FROM subject as su
JOIN species as sp
ON su.species_id = sp.species_id;

