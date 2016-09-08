# Autosave stuff

import json, os

from portal.db import Database, DBSession
db = Database()

Students = db.table_string_to_class('student')
Teachers = db.table_string_to_class('advisor')

class Model:

    def __init__(self, teachers=[]):
        self._data = {}
        self._teachers = teachers
        with DBSession() as session:
            for teacher_id in self._teachers:
                teacher = session.query(Teachers).filter_by(id=teacher_id).one()
                self.init_teacher(teacher)

    def init_teacher(self, teacher):
        self._data[teacher.id] = {'teacher': teacher, 'students':[]}

    def unpack_json(self, data):
        """
        One-offer
        """
        with DBSession() as session:
            for teacher_id in data:
                teacher = session.query(Teachers).filter_by(id=teacher_id).one()
                self.init_teacher(teacher)
                for student_id in data[teacher_id]:
                    student = session.query(Students).filter_by(id=student_id).one()
                    self.add_student_to_teacher(student, teacher)

    def take_data(self, data):
        self._data = data

    def add_student_to_teacher(self, student, teacher):
        self._data[teacher.id]['students'].append(student)

    def move_student(self, teacher_id, student_id):
        """
        Adds or moves student
        """
        with DBSession() as session:
            teacher = session.query(Teachers).filter_by(id=teacher_id).one()
            student = session.query(Students).filter_by(student_id=student_id).one()

        to_remove = []
        for teacher_key in self._data:
            students_ids = [s.student_id for s in self._data[teacher_key]['students']]
            if student_id in students_ids:
                to_remove.append( (teacher_key, students_ids.index(student_id)) )

        if len(to_remove) == 1:
            k, i = to_remove[0]
            del self._data[k]['students'][i]

        self.add_student_to_teacher(student, teacher)

    def dump(self):
        data = {}
        for teacher_key in self._data.keys():
            data[teacher_key] = []
            for student in self._data[teacher_key]['students']:
                data[teacher_key].append( student.id )
        return data

    def string_dump(self):
        data = {}
        for teacher_key in self._data.keys():
            data[int(str(teacher_key))] = []
            for student in self._data[teacher_key]['students']:
                data[int(str(teacher_key))].append( int(str(student.id)) )
        return data        

    def display(self): 
        for teacher_key in self._data:
            teacher = self._data[teacher_key]['teacher']
            print(u"{0.first_name} {0.last_name} [{0.id}]".format(teacher))
            students = self._data[teacher_key]['students']
            students.sort(key=lambda s:(s.grade, s.nickname_last_studentid))
            for student in students:
                print(u"   ({0.grade}) {0.nickname_last_studentid}".format(student))

class Saved:
    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        return os.path.join(self._path, 'data.json')

    def save(self, data):
        with open(self.path, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)

    def read(self):
        with open(self.path, 'r') as fp:
            data = json.load(fp)
        return data


if __name__ == "__main__":

    m = Model()
    #m.unpack_json({11256632: [11204340, 11173388, 11203889, 11324799, 11203892, 11490303, 11203911, 11471843, 11204634, 11203902, 11204319, 11124222, 10893375, 11080391, 11135112, 10856826, 10834635, 10866876, 10837001, 11190340, 11270692, 11135108, 11204641, 10834640, 10834616, 10866877, 10865037, 10856824, 10834636, 11324785, 11204392, 10834628, 10836994, 11153068, 10986488, 11124212, 11274134, 10856823, 10866874, 11204383, 11426392, 11274137, 10863222, 10834643, 10834648, 11201785, 11203952, 10834651, 11203979, 10912649, 11538429, 11563304, 10867796, 11203954, 10863230, 11204001, 11204000, 10882162, 10837002, 11200870, 11204385, 11203950, 10973671, 11204008, 10834633, 11182305, 10882159, 11609996, 10868400, 11204026, 11221516, 10856827, 10882152, 11153067, 11203997, 11204401], 11303618: [11124209, 11204331, 11392152, 11153071, 11203893, 11124216, 11203938, 11203926, 11203933, 11502297, 10834649, 11203970, 10882226, 10834617, 11124223, 10836999, 10882227, 11204637, 11203961, 11190071, 11182291, 10834621, 10867797, 11203923, 10882225, 11124215, 11124210, 10834630, 11476123, 11204631, 10834618, 10834622, 11203946, 10893379, 11153066, 11203988, 10856636, 10834625, 11124219, 11204640, 11204609, 11173915, 11204605, 10834645, 11364525, 11274131, 11080380, 10913691, 10834642, 10834661, 10866873, 11182284, 11204017, 11204377, 10912651, 11135103, 11464377, 11274132, 11204035, 11201788, 10834637, 10908165, 11124218, 11274133, 10834656, 11153073, 11173912, 11204044, 11204303, 10836998]})
    store = Saved('/tmp/test')
    j = store.read()
    m.unpack_json(j)

    done = False
    while not done:
        #m.display_teachers()
        choice = raw_input('Enter: ')
        choice = choice.strip('\n')
        if choice == 'X':
            done = True
        if choice == 'O':
            j = m.string_dump()
            print(j)
        if choice == 'D':
            m.display()
        if choice == 'A':
            student_id = raw_input('Enter student to move\'s Student ID: ')
            teacher_id = raw_input('Enter teacher to add to\'s ID: ')
            m.move_student(teacher_id, student_id)
        if choice == 'S':
            j = m.dump()
            store.save(j)
        if choice == 'M':
            student_id = raw_input('Enter student to move\'s Student ID: ')
            teacher_id = raw_input('Enter teacher to add to\'s ID: ')
            if not ' ' in student_id:
                m.move_student(teacher_id, student_id)
            else:
                sstudents = student_id.split(' ')
                for s in sstudents:
                    m.move_student(teacher_id, s)
