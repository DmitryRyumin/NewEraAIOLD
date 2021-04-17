#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Исключения NewEraAI
"""

class NewEraAIException(Exception):
    """Базовый класс для всех пользовательских исключений NewEraAI"""
    pass

class LanguagesSRError(NewEraAIException):
    """Указан неподдерживаемый язык для распознавания речи"""
    pass

class DictSRError(NewEraAIException):
    """Указан неподдерживаемый размер словаря для распознавания речи"""
    pass

class SRModelNotActivatedError(NewEraAIException):
    """Модель распознавания речи не активирована"""
    pass

class TypeEncodeVideoError(NewEraAIException):
    """Указан неподдерживаемый тип кодирования видео"""
    pass

class PresetCFREncodeVideoError(NewEraAIException):
    """Указан неподдерживаемый параметр обеспечивающий определенную скорость кодирования и сжатия видео"""
    pass

class SRInputTypeError(NewEraAIException):
    """Указан неподдерживаемый тип файла для распознавания речи"""
    pass

class IsADirectoryOriginalError(NewEraAIException):
    """Директории с оригинальными видео не найдена"""
    pass

class IsADirectorySplittedError(NewEraAIException):
    """Директории с разделенными видеофрагментами не найдена"""
    pass