import pytest
import tracemalloc
from unittest.mock import AsyncMock, patch
import unittest
from sqlalchemy.exc import DataError


import app.sup_func as sf
import app.handlers as h
import app.keyboards as kb
import app.database.requests as rq
import app.advanced_handlers as ah
from app.handlers import Reg
from app.advanced_handlers import Subjects, Timetable

tracemalloc.start()

class BotTest(unittest.TestCase):

    ### тест для проверки на возможность ковертирования
    def test_convert_into_group_number_negative(self):
        text = 'c'
        with pytest.raises(ValueError):
            self.assertRaises(sf.convert_into_group_number(text))

    def test_convert_into_group_number_positive(self):
        text = '241'
        self.assertTrue(sf.convert_into_group_number(text))


    ### тест для проверки на формат записи
    def test_check_date_positive(self):
        day = '01.01.2031 13:00'
        self.assertTrue(sf.check_date(day))

    def test_check_date_negative(self):
        day = '01.01.31 13:00'
        with pytest.raises(ValueError):
            self.assertRaises(sf.check_date(day))


    ### тест для проверки на положительность
    def test_check_value_positive(self):
        gap = 2
        self.assertTrue(sf.check_value(gap))

    def test_check_value_negative(self):
        gap = 'c'
        with pytest.raises(ValueError):
            self.assertRaises(sf.check_value(gap))


    def test_check_format_scheduler_positive(self):
        timetable = '1.Аип 2.Алгем\nЗанятий нет\nЗанятий нет\nЗанятий нет\nЗанятий нет\nЗанятий нет'
        self.assertTrue(sf.check_format_scheduler(timetable))

    def test_check_format_scheduler_negative(self):
        timetable = 'Аип 2.Алгем\nЗанятий нет\nЗанятий нет\nЗанятий нет\nЗанятий нет\nЗанятий нет'
        with pytest.raises(ValueError):
            self.assertRaises(sf.check_format_scheduler(timetable))

    
### тест для проверки на длину строки в write_student_name
@pytest.mark.asyncio
async def test_write_student_name_negative():
        message = AsyncMock()
        message.text = 'fjfjff' * 30
        group = 242
        state = AsyncMock()
        message.from_user.id = 542241668

        await ah.write_student_name(message, state)

        with pytest.raises(DataError):
            await rq.set_group_list(message.text, group)
            message.answer.called_with('Имя слишком длинное.\nМаксимальная длина вводимых данных: 40 символов')


@pytest.mark.asyncio
async def test_write_student_name_positive():
    message = AsyncMock()
    message.text = 'Закончить'
    state = AsyncMock()
    message.from_user.id = 542241668

    
    await ah.write_student_name(message, state)

    await message.answer.called_with('Что надо?',
                             reply_markup=kb.main)


import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import DataError

@pytest.mark.asyncio
async def test_reg_name_negative():
    message = AsyncMock()
    message.text = 'fjfjff' * 30
    state = AsyncMock()
    message.from_user.id = 542241668

    with patch("app.database.requests.set_user", new_callable=AsyncMock) as mock_set_user, \
         patch("app.keyboards.main", new_callable=AsyncMock) as mock_kb_main:

        mock_set_user.side_effect = DataError("Error", None, None)
        mock_kb_main.return_value = "MockedKeyboard"

        await h.reg_name(message, state)

        message.answer.assert_awaited_with(
            'Имя слишком длинное.\nМаксимальная длина вводимых данных: 40 символов')
        state.set_state.assert_awaited_once_with(Reg.name)
        mock_set_user.assert_awaited_once()

    


@pytest.mark.asyncio
async def test_reg_name_positive():
    message = AsyncMock()
    message.text = "София Кузнецова"
    state = AsyncMock()
    message.from_user.id = 542241668

    with patch("app.database.requests.set_user", new_callable=AsyncMock) as mock_set_user, \
         patch("app.keyboards.main", new_callable=AsyncMock) as mock_kb_main:

        mock_kb_main.return_value = "MockedKeyboard"

        await h.reg_name(message, state)

        message.answer.assert_awaited_with('Вроде зарегистрировались.\nЧто надо?', reply_markup= await kb.main(message.from_user.id))
        mock_set_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_subject_negative():
    message = AsyncMock()
    state = AsyncMock()
    message.text = 'абобаafqfqfqffewfrgeigjwvrvuevmwemvevmf4wffwefgqw4tgeqgqgqgg5gq5ghqh5hq'
    state.set_state = AsyncMock()

    '''    with pytest.raises(DataError):
        await ah.add_subject(message, state)'''
    with patch("app.database.requests.add_subject") as mock_add_subject:
        mock_add_subject.side_effect = DataError("Error", None, None)

        await ah.add_subject(message, state)

        message.answer.assert_awaited_with('Предмет слишком длинный.\nДопустимая длина вводимых данных: 120 символов')  
        state.set_state.assert_called_with(Subjects.subject)


@pytest.mark.asyncio
async def test_add_subject_positive():
    message = AsyncMock()
    state = AsyncMock()
    message.text = 'абоба'
    state.set_state = AsyncMock()

    with patch("app.database.requests.add_subject") as mock_add_subject:
        

        await ah.add_subject(message, state)
        mock_add_subject.assert_awaited_once_with(message.text)
        state.set_state.assert_awaited_with(Subjects.subject)



    





    



